import re
import unicodedata
from datetime import date

_NAME_CHARS = re.compile(r"[^\w\s'’.\-]", re.UNICODE)
_DATE = re.compile(r"(\d{1,2})\s*[./\-]\s*(\d{1,2})\s*[./\-]\s*(\d{4})")
_HEIGHT = re.compile(r"^([0-2])\s*[.,]\s*(\d{2})$")
_DIGIT_FIX = str.maketrans({"O": "0", "o": "0", "I": "1", "l": "1", "|": "1", "S": "5", "B": "8"})


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def canonical(text: str) -> str:
    """Forme comparable : sans accents, majuscules, espaces compactés."""
    return " ".join(strip_accents(text).upper().split())


def clean_name(text: str | None, *, max_length: int = 80) -> str | None:
    if not text:
        return None
    cleaned = " ".join(_NAME_CHARS.sub("", text).split())
    letters = sum(c.isalpha() for c in cleaned)
    if letters < 2 or letters < len(cleaned) * 0.7 or len(cleaned) > max_length:
        return None
    return cleaned


def clean_text(text: str | None, *, max_length: int = 80) -> str | None:
    if not text:
        return None
    cleaned = " ".join(_NAME_CHARS.sub("", text).split())
    return cleaned[:max_length] if cleaned else None


def parse_date(text: str | None) -> date | None:
    """Accepte jj.mm.aaaa, jj/mm/aaaa et jj-mm-aaaa avec corrections des confusions OCR courantes."""
    if not text:
        return None
    candidate = text.translate(_DIGIT_FIX)
    match = _DATE.search(candidate)
    if not match:
        return None
    day, month, year = (int(g) for g in match.groups())
    try:
        return date(year, month, day)
    except ValueError:
        return None


def parse_sex(text: str | None) -> str | None:
    if not text:
        return None
    value = canonical(text)
    return value if value in {"M", "F"} else None


def parse_height_m(text: str | None) -> float | None:
    if not text:
        return None
    match = _HEIGHT.match(text.strip())
    if not match:
        return None
    height = float(f"{match.group(1)}.{match.group(2)}")
    return height if 0.5 <= height <= 2.6 else None


def full_years(born: date, today: date) -> int:
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
