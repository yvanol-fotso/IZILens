import io
import uuid

import numpy as np
import pytest
from fastapi import UploadFile
from PIL import Image

from app.core.crypto import DataCipher
from app.core.exceptions import PayloadTooLarge, UnsupportedMedia, ValidationFailed
from app.shared.ocr.engine import parse_paddle_result
from app.shared.storage.base import StorageError
from app.shared.storage.local import LocalEncryptedStorage
from app.shared.validation.files import normalize_image, read_upload
from tests.helpers import make_image

LIMITS = {"min_long_side": 800, "min_short_side": 450}


def test_valid_png_is_normalized_to_jpeg_without_metadata():
    image = normalize_image(make_image(1), **LIMITS)
    assert image.mime_type == "image/jpeg" and image.data.startswith(b"\xff\xd8\xff") and len(image.sha256) == 64
    assert image.sharpness > 25


def test_same_input_gives_same_hash_and_other_input_differs():
    assert normalize_image(make_image(1), **LIMITS).sha256 == normalize_image(make_image(1), **LIMITS).sha256
    assert normalize_image(make_image(1), **LIMITS).sha256 != normalize_image(make_image(2), **LIMITS).sha256


def test_exif_is_stripped():
    source = Image.fromarray(np.random.default_rng(3).integers(0, 255, (648, 1024, 3), dtype=np.uint8))
    exif = Image.Exif()
    exif[0x010E] = "donnée-personnelle"
    buffer = io.BytesIO()
    source.save(buffer, format="JPEG", exif=exif)
    cleaned = normalize_image(buffer.getvalue(), **LIMITS)
    assert b"donn" not in cleaned.data and len(Image.open(io.BytesIO(cleaned.data)).getexif()) == 0


@pytest.mark.parametrize("payload", [b"GIF89a" + b"0" * 100, b"%PDF-1.7 fake", b"<script>alert(1)</script>", b"MZ" + b"0" * 100])
def test_wrong_signature_rejected(payload):
    with pytest.raises(UnsupportedMedia):
        normalize_image(payload, **LIMITS)


def test_corrupted_png_rejected():
    with pytest.raises(ValidationFailed):
        normalize_image(make_image(1)[:300], **LIMITS)


def test_png_signature_with_garbage_rejected():
    with pytest.raises(ValidationFailed):
        normalize_image(b"\x89PNG\r\n\x1a\n" + b"garbage" * 50, **LIMITS)


def test_small_image_rejected():
    with pytest.raises(ValidationFailed) as error:
        normalize_image(make_image(1, size=(400, 300)), **LIMITS)
    assert error.value.code == "IMAGE_TOO_SMALL"


def test_large_image_is_downscaled():
    result = normalize_image(make_image(1, size=(3200, 2000), fmt="JPEG"), **LIMITS)
    assert max(result.width, result.height) == 2400


def test_read_upload_enforces_size_and_rejects_empty():
    with pytest.raises(PayloadTooLarge):
        read_upload(UploadFile(io.BytesIO(b"x" * 101), filename="a.png"), 100)
    with pytest.raises(ValidationFailed):
        read_upload(UploadFile(io.BytesIO(b""), filename="a.png"), 100)
    assert read_upload(UploadFile(io.BytesIO(b"x" * 100), filename="a.png"), 100) == b"x" * 100


def test_storage_encrypts_at_rest_and_roundtrips(tmp_path):
    from cryptography.fernet import Fernet

    storage = LocalEncryptedStorage(tmp_path, DataCipher([Fernet.generate_key().decode()]))
    org, case = uuid.uuid4(), uuid.uuid4()
    key = storage.save(organization_id=org, case_id=case, data=b"SECRET-IMAGE-BYTES")
    assert b"SECRET-IMAGE-BYTES" not in (tmp_path / key).read_bytes()
    assert storage.load(key) == b"SECRET-IMAGE-BYTES"
    storage.delete(key)
    with pytest.raises(StorageError):
        storage.load(key)


def test_storage_rejects_path_traversal(tmp_path):
    from cryptography.fernet import Fernet

    storage = LocalEncryptedStorage(tmp_path / "root", DataCipher([Fernet.generate_key().decode()]))
    for key in ("../outside.bin", "/etc/passwd", "a/../../b"):
        with pytest.raises(StorageError):
            storage.load(key)


def test_cipher_supports_key_rotation():
    from cryptography.fernet import Fernet

    old, new = Fernet.generate_key().decode(), Fernet.generate_key().decode()
    token = DataCipher([old]).encrypt(b"data")
    assert DataCipher([new, old]).decrypt(token) == b"data"


def test_parse_paddle_result_with_boxes_and_polygon_fallback():
    with_boxes = [{"rec_texts": ["A", " "], "rec_scores": [0.9, 0.5], "rec_boxes": np.array([[1, 2, 30, 40], [0, 0, 1, 1]])}]
    lines = parse_paddle_result(with_boxes)
    assert len(lines) == 1 and (lines[0].x1, lines[0].y2, lines[0].score) == (1.0, 40.0, 0.9)
    with_polys = [{"rec_texts": ["B"], "rec_scores": [0.8], "rec_polys": [np.array([[5, 6], [50, 6], [50, 20], [5, 20]])]}]
    assert parse_paddle_result(with_polys)[0].x2 == 50.0
