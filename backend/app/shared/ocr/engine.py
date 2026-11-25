import io
import logging
import threading
from typing import Any

import numpy as np
from PIL import Image

from app.core.config import get_settings
from app.shared.ocr.types import OcrEngine, OcrLine

logger = logging.getLogger("app.ocr")


def parse_paddle_result(results: Any) -> list[OcrLine]:
    """Convertit la sortie PaddleOCR 3.x en lignes typées avec boîtes englobantes."""
    lines: list[OcrLine] = []
    for page in results:
        texts, scores = page["rec_texts"], page["rec_scores"]
        try:
            boxes = [[float(v) for v in box] for box in page["rec_boxes"]]
        except KeyError:
            boxes = []
            for polygon in page["rec_polys"]:
                xs, ys = [float(p[0]) for p in polygon], [float(p[1]) for p in polygon]
                boxes.append([min(xs), min(ys), max(xs), max(ys)])
        for text, score, box in zip(texts, scores, boxes, strict=False):
            if str(text).strip():
                lines.append(OcrLine(str(text).strip(), float(score), box[0], box[1], box[2], box[3]))
    return lines


class PaddleOcrEngine:
    """Enveloppe PaddleOCR : chargement paresseux unique et inférence sérialisée (modèle non thread-safe)."""

    def __init__(self, lang: str) -> None:
        self._lang = lang
        self._ocr: Any = None
        self._load_lock = threading.Lock()
        self._run_lock = threading.Lock()

    def load(self) -> None:
        with self._load_lock:
            if self._ocr is None:
                from paddleocr import PaddleOCR

                logger.info("Chargement des modèles OCR")
                self._ocr = PaddleOCR(
                    lang=self._lang,
                    use_doc_orientation_classify=False,
                    use_doc_unwarping=False,
                    use_textline_orientation=False,
                    enable_mkldnn=False,
                )

    def read(self, image_bytes: bytes) -> list[OcrLine]:
        self.load()
        with Image.open(io.BytesIO(image_bytes)) as image:
            bgr = np.asarray(image.convert("RGB"))[:, :, ::-1].copy()
        with self._run_lock:
            results = self._ocr.predict(bgr)
        return parse_paddle_result(results)


_engine: OcrEngine | None = None
_engine_lock = threading.Lock()


def get_engine() -> OcrEngine:
    global _engine
    with _engine_lock:
        if _engine is None:
            _engine = PaddleOcrEngine(get_settings().ocr_lang)
        return _engine


def set_engine(engine: OcrEngine | None) -> None:
    """Injecte un moteur de substitution (tests) ou réinitialise le moteur par défaut."""
    global _engine
    with _engine_lock:
        _engine = engine
