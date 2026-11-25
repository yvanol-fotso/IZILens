import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from statistics import median

from app.shared.ocr.types import OcrLine
from app.shared.validation.fields import strip_accents

LABEL_MATCH_RATIO = 0.80

_LABELS: dict[str, tuple[str, ...]] = {
    "surname": ("NOMSURNAME", "SURNAME"),
    "given_names": ("PRENOMSGIVENNAMES", "GIVENNAMES"),
    "date_of_birth": ("DATEDENAISSANCEDATEOFBIRTH", "DATEOFBIRTH"),
    "place_of_birth": ("LIEUDENAISSANCEPLACEOFBIRTH", "PLACEOFBIRTH"),
    "sex": ("SEXESEX",),
    "height": ("TAILLEHEIGHT", "HEIGHT"),
    "profession": ("PROFESSIONOCCUPATION", "OCCUPATION"),
    "date_of_expiry": ("DATEDEXPIRATIONDATEOFEXPIRY", "DATEOFEXPIRY", "EXPIRYDATE"),
    "signature": ("SIGNATURE",),
}
_HEADERS = ("REPUBLIQUEDUCAMEROUN", "REPUBLICOFCAMEROON", "CARTENATIONALEDIDENTITE", "NATIONALIDENTITYCARD")
_SEX_VALUE = re.compile(r"^[MF]$")
_HEIGHT_VALUE = re.compile(r"^[0-2]\s*[.,]\s*\d{2}$")
STACKED_FIELDS = ("surname", "given_names", "date_of_birth", "place_of_birth", "profession")


@dataclass(frozen=True)
class RawField:
    text: str
    score: float
    method: str  # "label" : trouvé sous son étiquette ; "inferred" : déduit de sa position


@dataclass(frozen=True)
class CniExtraction:
    fields: dict[str, RawField]
    header_found: bool
    line_count: int


def _norm(text: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", strip_accents(text).upper())


def _ratio(text: str, aliases: tuple[str, ...]) -> float:
    normalized = _norm(text)
    return max((SequenceMatcher(None, normalized, alias).ratio() for alias in aliases), default=0.0) if normalized else 0.0


def _find_labels(lines: list[OcrLine]) -> dict[str, OcrLine]:
    found: dict[str, OcrLine] = {}
    for field, aliases in _LABELS.items():
        ranked = sorted(((_ratio(line.text, aliases), line) for line in lines), key=lambda item: -item[0])
        if ranked and ranked[0][0] >= LABEL_MATCH_RATIO:
            found[field] = ranked[0][1]
    return found


def _is_header(line: OcrLine) -> bool:
    return _ratio(line.text, _HEADERS) >= LABEL_MATCH_RATIO


def _aligned(label: OcrLine, line: OcrLine) -> bool:
    overlap = min(label.x2, line.x2) - max(label.x1, line.x1)
    return overlap > 0 and abs(line.x1 - label.x1) <= max(60.0, label.width * 0.5)


def _value_below(label: OcrLine, candidates: list[OcrLine]) -> OcrLine | None:
    best: OcrLine | None = None
    best_gap = float("inf")
    for line in candidates:
        gap = line.y1 - label.y2
        if line.center_y <= label.center_y or gap > 2.5 * max(label.height, line.height) or not _aligned(label, line):
            continue
        if gap < best_gap:
            best, best_gap = line, gap
    return best


def _band(candidates: list[OcrLine], top: float, bottom: float) -> list[OcrLine]:
    return sorted((ln for ln in candidates if ln.y1 >= top - 3 and ln.y2 <= bottom + 3), key=lambda ln: ln.y1)


def extract_cni_cameroun(lines: list[OcrLine], min_line_score: float = 0.3) -> CniExtraction:
    """Extrait les champs du recto d'une CNI camerounaise par étiquettes bilingues, avec repli positionnel."""
    lines = [ln for ln in lines if ln.score >= min_line_score and ln.text.strip()]
    labels = _find_labels(lines)
    label_ids = {id(ln) for ln in labels.values()}
    noise_ids = label_ids | {id(ln) for ln in lines if _is_header(ln)}
    values = [ln for ln in lines if id(ln) not in noise_ids]
    fields: dict[str, RawField] = {}
    anchors: dict[str, OcrLine] = {}

    for name in ("surname", "given_names", "date_of_birth", "place_of_birth", "profession", "date_of_expiry"):
        label = labels.get(name)
        line = _value_below(label, values) if label else None
        if line:
            fields[name] = RawField(line.text, line.score, "label")
            anchors[name] = line

    typical = median(a.height for a in anchors.values()) if anchors else 0.0

    def infer(name: str, previous: str, following: str | None) -> None:
        if name in fields or previous not in anchors:
            return
        top = anchors[previous].y2
        bottom = labels[following].y1 if following in labels else float("inf")
        band = [ln for ln in _band(values, top, bottom) if ln.height >= 0.75 * typical]
        if band:
            fields[name] = RawField(band[0].text, band[0].score, "inferred")
            anchors[name] = band[0]

    infer("place_of_birth", "date_of_birth", "sex")
    infer("place_of_birth", "date_of_birth", "profession")

    floor = (
        anchors["place_of_birth"].y2
        if "place_of_birth" in anchors
        else (anchors["date_of_birth"].y2 if "date_of_birth" in anchors else 0.0)
    )
    ceiling = (
        labels["profession"].y1 if "profession" in labels else (labels["signature"].y1 if "signature" in labels else float("inf"))
    )
    row = _band(values, floor, ceiling)

    sex_label = labels.get("sex")
    sex_line = _value_below(sex_label, values) if sex_label else None
    if sex_line is None or not _SEX_VALUE.match(_norm(sex_line.text)):
        sex_line = next((ln for ln in row if _SEX_VALUE.match(_norm(ln.text))), None)
        method = "inferred"
    else:
        method = "label"
    if sex_line:
        fields["sex"] = RawField(sex_line.text, sex_line.score, method)

    height_line = next((ln for ln in row if _HEIGHT_VALUE.match(ln.text.strip())), None)
    if height_line:
        fields["height"] = RawField(height_line.text, height_line.score, "label" if "height" in labels else "inferred")

    infer("profession", "place_of_birth" if "place_of_birth" in anchors else "date_of_birth", "signature")

    return CniExtraction(fields=fields, header_found=any(_is_header(ln) for ln in lines), line_count=len(lines))
