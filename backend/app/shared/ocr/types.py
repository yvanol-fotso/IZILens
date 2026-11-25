from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class OcrLine:
    text: str
    score: float
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def height(self) -> float:
        return max(self.y2 - self.y1, 1.0)

    @property
    def width(self) -> float:
        return max(self.x2 - self.x1, 1.0)

    @property
    def center_y(self) -> float:
        return (self.y1 + self.y2) / 2


class OcrEngine(Protocol):
    def read(self, image_bytes: bytes) -> list[OcrLine]: ...
