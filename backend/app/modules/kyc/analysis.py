from dataclasses import dataclass, field
from datetime import date

from app.common.constants import SHARPNESS_MIN
from app.common.enums import FlagSeverity, RiskLevel
from app.core.security import keyed_digest
from app.shared.ocr.cni_cameroun import CniExtraction, extract_cni_cameroun
from app.shared.ocr.types import OcrLine
from app.shared.validation import fields as fv

REQUIRED_FIELDS = ("surname", "given_names", "date_of_birth")
OPTIONAL_FIELDS = ("place_of_birth", "sex", "height", "profession")
MINIMUM_AGE = 18
_FIELD_LABELS = {
    "surname": "nom",
    "given_names": "prénoms",
    "date_of_birth": "date de naissance",
    "place_of_birth": "lieu de naissance",
    "sex": "sexe",
    "height": "taille",
    "profession": "profession",
}


@dataclass
class AnalysisResult:
    fields: dict[str, dict]
    flags: list[dict]
    risk_level: RiskLevel
    confidence: float | None
    identity_fingerprint: str | None
    extras: dict = field(default_factory=dict)


def _flag(code: str, severity: FlagSeverity, message: str, field_name: str | None = None) -> dict:
    flag = {"code": code, "severity": severity.value, "message": message}
    if field_name:
        flag["field"] = field_name
    return flag


def _normalize(name: str, raw_text: str, today: date) -> tuple[str | None, str | None]:
    """Retourne (valeur normalisée, code d'anomalie) pour un champ brut."""
    if name in ("surname", "given_names"):
        cleaned = fv.clean_name(raw_text)
        return cleaned, None if cleaned else "INVALID_NAME"
    if name == "date_of_birth":
        parsed = fv.parse_date(raw_text)
        if parsed is None or parsed >= today or fv.full_years(parsed, today) > 120:
            return None, "INVALID_DATE_OF_BIRTH"
        return parsed.isoformat(), None
    if name == "sex":
        sex = fv.parse_sex(raw_text)
        return sex, None if sex else "INVALID_SEX"
    if name == "height":
        height = fv.parse_height_m(raw_text)
        return (f"{height:.2f}" if height else None), None if height else "INVALID_HEIGHT"
    cleaned = fv.clean_text(raw_text)
    return cleaned, None if cleaned else "INVALID_TEXT"


def analyze_front(
    lines: list[OcrLine], *, sharpness: float, today: date, review_threshold: float, min_line_score: float
) -> AnalysisResult:
    """Transforme les lignes OCR du recto en champs validés, signaux de risque et niveau de risque."""
    extraction: CniExtraction = extract_cni_cameroun(lines, min_line_score)
    flags: list[dict] = []
    fields: dict[str, dict] = {}

    if extraction.line_count == 0:
        flags.append(_flag("NO_TEXT_DETECTED", FlagSeverity.HIGH, "Aucun texte détecté sur le document"))
    elif not extraction.header_found:
        flags.append(
            _flag("DOCUMENT_TYPE_UNRECOGNIZED", FlagSeverity.HIGH, "Le document ne ressemble pas à une CNI camerounaise")
        )
    if sharpness < SHARPNESS_MIN:
        flags.append(_flag("LOW_SHARPNESS", FlagSeverity.MEDIUM, "Image floue, lecture potentiellement dégradée"))

    for name in (*REQUIRED_FIELDS, *OPTIONAL_FIELDS):
        raw = extraction.fields.get(name)
        label = _FIELD_LABELS[name]
        required = name in REQUIRED_FIELDS
        if raw is None:
            fields[name] = {"value": None, "normalized": None, "score": None, "method": None, "valid": False}
            flags.append(
                _flag(
                    "MISSING_FIELD",
                    FlagSeverity.HIGH if required else FlagSeverity.MEDIUM,
                    f"Champ « {label} » introuvable",
                    name,
                )
            )
            continue
        normalized, issue = _normalize(name, raw.text, today)
        fields[name] = {
            "value": raw.text,
            "normalized": normalized,
            "score": round(raw.score, 4),
            "method": raw.method,
            "valid": issue is None,
        }
        if issue:
            severity = FlagSeverity.HIGH if required else FlagSeverity.LOW
            flags.append(_flag(issue, severity, f"Valeur invalide pour « {label} »", name))
        if raw.score < review_threshold:
            severity = FlagSeverity.HIGH if raw.score < 0.6 else FlagSeverity.MEDIUM
            flags.append(_flag("LOW_CONFIDENCE", severity, f"Lecture peu fiable pour « {label} » ({raw.score:.0%})", name))
        if raw.method == "inferred":
            flags.append(_flag("INFERRED_FIELD", FlagSeverity.LOW, f"« {label} » déduit de sa position sur la carte", name))

    birth = fields["date_of_birth"]["normalized"]
    if birth and fv.full_years(date.fromisoformat(birth), today) < MINIMUM_AGE:
        flags.append(_flag("UNDERAGE", FlagSeverity.HIGH, "Le titulaire est mineur", "date_of_birth"))

    scores = [fields[n]["score"] for n in REQUIRED_FIELDS if fields[n]["score"] is not None]
    confidence = round(min(scores), 4) if len(scores) == len(REQUIRED_FIELDS) else None

    fingerprint = None
    if all(fields[n]["normalized"] for n in REQUIRED_FIELDS):
        identity = "|".join(
            (fv.canonical(fields["surname"]["normalized"]), fv.canonical(fields["given_names"]["normalized"]), birth)
        )
        fingerprint = keyed_digest(identity)

    return AnalysisResult(fields, flags, compute_risk(flags), confidence, fingerprint)


def compute_risk(flags: list[dict]) -> RiskLevel:
    severities = {f["severity"] for f in flags}
    if FlagSeverity.HIGH.value in severities:
        return RiskLevel.HIGH
    if FlagSeverity.MEDIUM.value in severities:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def add_flag(result_flags: list[dict], code: str, severity: FlagSeverity, message: str, **extra: object) -> None:
    result_flags.append({**_flag(code, severity, message), **extra})
