import hashlib
import io
from dataclasses import dataclass

import numpy as np
from fastapi import UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

from app.common.constants import (
    ALLOWED_IMAGE_FORMATS,
    IMAGE_SIGNATURES,
    MAX_IMAGE_PIXELS,
    MAX_IMAGE_SIDE_PX,
)
from app.core.exceptions import PayloadTooLarge, UnsupportedMedia, ValidationFailed

Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


@dataclass(frozen=True)
class NormalizedImage:
    data: bytes
    mime_type: str
    width: int
    height: int
    sha256: str
    sharpness: float


def read_upload(upload: UploadFile, max_bytes: int) -> bytes:
    """Lit le fichier avec plafond strict, sans jamais charger plus que la limite autorisée."""
    data = upload.file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise PayloadTooLarge(f"Fichier supérieur à {max_bytes // (1024 * 1024)} Mo", code="FILE_TOO_LARGE")
    if not data:
        raise ValidationFailed("Fichier vide", code="EMPTY_FILE")
    return data


def _sharpness(image: Image.Image) -> float:
    """Variance du laplacien sur l'image en niveaux de gris : faible valeur = image floue."""
    gray = ImageOps.grayscale(image)
    scale = 1000 / max(gray.size)
    if scale < 1:
        gray = gray.resize((int(gray.width * scale), int(gray.height * scale)), Image.Resampling.BILINEAR)
    pixels = np.asarray(gray, dtype=np.float32)
    laplacian = -4 * pixels[1:-1, 1:-1] + pixels[:-2, 1:-1] + pixels[2:, 1:-1] + pixels[1:-1, :-2] + pixels[1:-1, 2:]
    return float(laplacian.var())


def normalize_image(raw: bytes, *, min_long_side: int, min_short_side: int) -> NormalizedImage:
    """Valide le contenu réel, corrige l'orientation, supprime les métadonnées et ré-encode en JPEG."""
    if not raw.startswith(IMAGE_SIGNATURES):
        raise UnsupportedMedia("Format non supporté (JPEG ou PNG uniquement)", code="UNSUPPORTED_IMAGE_FORMAT")
    try:
        with Image.open(io.BytesIO(raw)) as probe:
            probe.verify()
        with Image.open(io.BytesIO(raw)) as opened:
            if opened.format not in ALLOWED_IMAGE_FORMATS:
                raise UnsupportedMedia("Format non supporté (JPEG ou PNG uniquement)", code="UNSUPPORTED_IMAGE_FORMAT")
            image = ImageOps.exif_transpose(opened).convert("RGB")
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, SyntaxError) as exc:
        raise ValidationFailed("Image illisible ou corrompue", code="INVALID_IMAGE") from exc

    long_side, short_side = max(image.size), min(image.size)
    if long_side < min_long_side or short_side < min_short_side:
        raise ValidationFailed(f"Résolution insuffisante (minimum {min_long_side}x{min_short_side} px)", code="IMAGE_TOO_SMALL")
    if long_side > MAX_IMAGE_SIDE_PX:
        ratio = MAX_IMAGE_SIDE_PX / long_side
        image = image.resize((round(image.width * ratio), round(image.height * ratio)), Image.Resampling.LANCZOS)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=92, optimize=True)
    data = buffer.getvalue()
    return NormalizedImage(
        data=data,
        mime_type="image/jpeg",
        width=image.width,
        height=image.height,
        sha256=hashlib.sha256(data).hexdigest(),
        sharpness=round(_sharpness(image), 2),
    )
