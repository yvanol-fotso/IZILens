import io

import numpy as np
from PIL import Image

from app.shared.ocr.types import OcrLine


class FakeEngine:
    def __init__(self, lines: list[OcrLine] | Exception) -> None:
        self.lines = lines
        self.calls = 0

    def read(self, image_bytes: bytes) -> list[OcrLine]:
        self.calls += 1
        if isinstance(self.lines, Exception):
            raise self.lines
        return self.lines


def line(text: str, score: float, x1: float, y1: float, x2: float, y2: float) -> OcrLine:
    return OcrLine(text, score, x1, y1, x2, y2)


def cni_lines(
    surname: str = "Atángana Mohammadou",
    given: str = "SALAH",
    dob: str = "15.06.1992",
    place: str = "Baffousam",
    profession: str = "Footballer",
    place_label_readable: bool = False,
    header: bool = True,
) -> list[OcrLine]:
    """Sortie OCR reconstituée à partir de la CNI de test (1024x648), étiquette du lieu de naissance illisible."""
    lines = [line("AAD", 0.63, 30, 20, 60, 40)]
    if header:
        lines += [line("RÉPUBLIQUE DU CAMEROUN", 1.0, 305, 25, 840, 60), line("REPUBLIC OF CAMEROON", 0.99, 305, 68, 808, 98)]
    lines += [
        line("NOMSURNAME", 1.0, 285, 125, 405, 138),
        line(surname, 0.96, 280, 148, 545, 178),
        line("PHENOMS/GIVENNAMES", 0.98, 285, 208, 470, 222),
        line(given, 1.0, 290, 232, 410, 262),
        line("DATEOFBIRTH", 0.96, 288, 293, 558, 306),
        line(dob, 1.0, 295, 312, 455, 340),
        line(
            "LIEU DE NAISSANCE/PLACE OF BIRTH" if place_label_readable else "ÉRITE",
            0.9 if place_label_readable else 0.69,
            290,
            343,
            560,
            356,
        ),
        line(place, 1.0, 303, 360, 505, 385),
        line("SERE/SEX", 0.94, 290, 396, 345, 408),
        line("M", 1.0, 290, 415, 300, 432),
        line("1.75", 1.0, 408, 415, 480, 432),
        line("PROFESSION/OCCUPATION", 0.99, 290, 441, 485, 455),
        line(profession, 1.0, 285, 460, 485, 488),
        line("SIGNATURE", 1.0, 285, 492, 372, 506),
    ]
    return lines


def make_image(seed: int = 1, size: tuple[int, int] = (1024, 648), fmt: str = "PNG") -> bytes:
    """Image synthétique texturée (donc nette) ; la graine distingue deux images."""
    rng = np.random.default_rng(seed)
    pixels = rng.integers(0, 255, size=(size[1], size[0], 3), dtype=np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(pixels).save(buffer, format=fmt)
    return buffer.getvalue()


DECLARED = {"declared_surname": "Atangana Mohammadou", "declared_given_names": "Salah", "declared_date_of_birth": "1992-06-15"}
BASE_FORM = {"country_code": "CM", "document_type": "cni_cm", "language": "fr"}


def form(**extra: str) -> dict:
    return {**BASE_FORM, **extra}


def files(front: bytes | None = None, back: bytes | None = None, name: str = "cni.png", mime: str = "image/png") -> dict:
    payload = {"front": (name, front if front is not None else make_image(), mime)}
    if back is not None:
        payload["back"] = ("back.png", back, mime)
    return payload


def make_flat_image(size: tuple[int, int] = (1024, 648)) -> bytes:
    """Image uniforme donc floue pour le contrôle de netteté."""
    buffer = io.BytesIO()
    Image.new("RGB", size, (128, 128, 128)).save(buffer, format="PNG")
    return buffer.getvalue()
