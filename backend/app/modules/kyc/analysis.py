from dataclasses import dataclass, field
from datetime import date

from app.common.constants import SHARPNESS_MIN
from app.common.enums import CheckStatus, CheckType, FlagSeverity, RiskLevel
from app.core.security import keyed_digest
from app.modules.kyc import matching
from app.shared.ocr.cni_cameroun import extract_cni_cameroun
from app.shared.ocr.types import OcrLine
from app.shared.validation import fields as fv

REQUIRED_FIELDS = ("surname", "given_names", "date_of_birth")
OPTIONAL_FIELDS = ("place_of_birth", "sex", "height", "profession")
MINIMUM_AGE = 18
LOW_SCORE_FLOOR = 0.6
EMPTY_FIELD = {"value": None, "normalized": None, "score": None, "method": None, "valid": False}


@dataclass
class CheckResult:
    check_type: CheckType
    status: CheckStatus
    details: dict = field(default_factory=dict)


@dataclass
class DocumentAnalysis:
    fields: dict[str, dict]
    checks: list[CheckResult]
    confidence: float | None
    identity_fingerprint: str | None


def _normalize(name: str, raw_text: str, today: date) -> tuple[str | None, str | None]:
    """Retourne (valeur normalisée, code d'anomalie) pour un champ brut."""
    if name in ("surname", "given_names"):
        cleaned = fv.clean_name(raw_text)
        return cleaned, None if cleaned else "INVALID_NAME"
    if name in ("date_of_birth", "date_of_expiry"):
        parsed = fv.parse_date(raw_text)
        if parsed is None:
            return None, "INVALID_DATE"
        if name == "date_of_birth" and (parsed >= today or fv.full_years(parsed, today) > 120):
            return None, "INVALID_DATE"
        return parsed.isoformat(), None
    if name == "sex":
        sex = fv.parse_sex(raw_text)
        return sex, None if sex else "INVALID_SEX"
    if name == "height":
        height = fv.parse_height_m(raw_text)
        return (f"{height:.2f}" if height else None), None if height else "INVALID_HEIGHT"
    cleaned = fv.clean_text(raw_text)
    return cleaned, None if cleaned else "INVALID_TEXT"


def declared_match_check(declared: dict | None, fields: dict[str, dict], thresholds: dict) -> CheckResult:
    if not declared:
        return CheckResult(CheckType.DECLARED_MATCH, CheckStatus.NOT_RUN, {"reason": "DECLARED_IDENTITY_MISSING"})
    if not all((fields.get(n) or {}).get("normalized") for n in REQUIRED_FIELDS):
        return CheckResult(CheckType.DECLARED_MATCH, CheckStatus.NOT_RUN, {"reason": "READ_DATA_INCOMPLETE"})
    comparison = matching.compare_identity(
        declared, fields, name_match=thresholds.get("name_match", 0.9), name_partial=thresholds.get("name_partial", 0.75)
    )
    return CheckResult(CheckType.DECLARED_MATCH, CheckStatus(matching.overall_status(comparison)), {"fields": comparison})


def analyze_document(
    lines: list[OcrLine], *, sharpness: float, today: date, thresholds: dict, min_line_score: float, declared: dict | None
) -> DocumentAnalysis:
    """Transforme les lignes OCR du recto en champs normalisés et en résultats de contrôles."""
    extraction = extract_cni_cameroun(lines, min_line_score)
    review_threshold = thresholds.get("ocr_review", 0.9)
    fields: dict[str, dict] = {}
    for name in (*REQUIRED_FIELDS, *OPTIONAL_FIELDS, "date_of_expiry"):
        raw = extraction.fields.get(name)
        if raw is None:
            fields[name] = dict(EMPTY_FIELD)
            continue
        normalized, issue = _normalize(name, raw.text, today)
        fields[name] = {
            "value": raw.text,
            "normalized": normalized,
            "score": round(raw.score, 4),
            "method": raw.method,
            "valid": issue is None,
        }

    checks = [
        CheckResult(
            CheckType.DOCUMENT_QUALITY,
            CheckStatus.PASSED if sharpness >= SHARPNESS_MIN else CheckStatus.FAILED,
            {"sharpness": sharpness, "minimum": SHARPNESS_MIN},
        )
    ]
    recognized = extraction.line_count > 0 and extraction.header_found
    if recognized:
        checks.append(CheckResult(CheckType.DOCUMENT_RECOGNITION, CheckStatus.PASSED))
    else:
        reason = "NO_TEXT" if extraction.line_count == 0 else "TYPE_UNRECOGNIZED"
        checks.append(CheckResult(CheckType.DOCUMENT_RECOGNITION, CheckStatus.FAILED, {"reason": reason}))

    missing = [n for n in REQUIRED_FIELDS if fields[n]["value"] is None]
    invalid = [n for n in REQUIRED_FIELDS if fields[n]["value"] is not None and not fields[n]["valid"]]
    weak = [
        n
        for n in REQUIRED_FIELDS
        if fields[n]["valid"] and ((fields[n]["score"] or 0) < review_threshold or fields[n]["method"] == "inferred")
    ]
    scores = [fields[n]["score"] for n in REQUIRED_FIELDS if fields[n]["score"] is not None]
    confidence = round(min(scores), 4) if len(scores) == len(REQUIRED_FIELDS) else None
    if not recognized:
        checks.append(CheckResult(CheckType.OCR_EXTRACTION, CheckStatus.NOT_RUN, {"reason": "DOCUMENT_NOT_RECOGNIZED"}))
    elif missing or invalid:
        checks.append(CheckResult(CheckType.OCR_EXTRACTION, CheckStatus.FAILED, {"missing": missing, "invalid": invalid}))
    elif weak:
        checks.append(CheckResult(CheckType.OCR_EXTRACTION, CheckStatus.INCONCLUSIVE, {"weak": weak, "confidence": confidence}))
    else:
        checks.append(CheckResult(CheckType.OCR_EXTRACTION, CheckStatus.PASSED, {"confidence": confidence}))

    checks.append(declared_match_check(declared, fields, thresholds))

    expiry = fields["date_of_expiry"]["normalized"]
    if expiry is None:
        checks.append(CheckResult(CheckType.EXPIRY, CheckStatus.NOT_RUN, {"reason": "NOT_DETERMINABLE"}))
    else:
        expired = date.fromisoformat(expiry) <= today
        checks.append(CheckResult(CheckType.EXPIRY, CheckStatus.FAILED if expired else CheckStatus.PASSED, {"expired": expired}))

    fingerprint = None
    if all(fields[n]["normalized"] for n in REQUIRED_FIELDS):
        identity = "|".join(
            (
                fv.canonical(fields["surname"]["normalized"]),
                fv.canonical(fields["given_names"]["normalized"]),
                fields["date_of_birth"]["normalized"],
            )
        )
        fingerprint = keyed_digest(identity)
    return DocumentAnalysis(fields, checks, confidence, fingerprint)


def _flag(code: str, severity: FlagSeverity, **extra: object) -> dict:
    return {"code": code, "severity": severity.value, **extra}


def derive_flags(fields: dict[str, dict] | None, checks: dict[str, dict], *, today: date, thresholds: dict) -> list[dict]:
    """Signaux de risque calculés à partir de l'état courant : jamais stockés comme source de vérité."""
    flags: list[dict] = []
    fields = fields or {}
    status = lambda t: checks.get(t.value, {}).get("status")  # noqa: E731
    details = lambda t: checks.get(t.value, {}).get("details", {})  # noqa: E731

    if status(CheckType.DOCUMENT_QUALITY) == "failed":
        flags.append(_flag("LOW_SHARPNESS", FlagSeverity.MEDIUM))
    if status(CheckType.DOCUMENT_RECOGNITION) == "failed":
        no_text = details(CheckType.DOCUMENT_RECOGNITION).get("reason") == "NO_TEXT"
        flags.append(_flag("NO_TEXT_DETECTED" if no_text else "DOCUMENT_TYPE_UNRECOGNIZED", FlagSeverity.HIGH))

    ocr = details(CheckType.OCR_EXTRACTION)
    for name in ocr.get("missing", []):
        flags.append(_flag("MISSING_FIELD", FlagSeverity.HIGH, field=name))
    for name in ocr.get("invalid", []):
        flags.append(_flag("INVALID_VALUE", FlagSeverity.HIGH, field=name))
    review_threshold = thresholds.get("ocr_review", 0.9)
    for name in (*REQUIRED_FIELDS, *OPTIONAL_FIELDS):
        data = fields.get(name) or {}
        if data.get("value") is None:
            if name in OPTIONAL_FIELDS and status(CheckType.DOCUMENT_RECOGNITION) == "passed":
                flags.append(_flag("MISSING_FIELD", FlagSeverity.MEDIUM, field=name))
            continue
        if not data.get("valid") and name in OPTIONAL_FIELDS:
            flags.append(_flag("INVALID_VALUE", FlagSeverity.LOW, field=name))
        score = data.get("score") or 0.0
        if score < review_threshold:
            severity = FlagSeverity.HIGH if score < LOW_SCORE_FLOOR else FlagSeverity.MEDIUM
            flags.append(_flag("LOW_CONFIDENCE", severity, field=name, score=score, score_label=f"{score:.0%}"))
        if data.get("method") == "inferred":
            flags.append(_flag("INFERRED_FIELD", FlagSeverity.LOW, field=name))

    birth = (fields.get("date_of_birth") or {}).get("normalized")
    if birth and fv.full_years(date.fromisoformat(birth), today) < MINIMUM_AGE:
        flags.append(_flag("UNDERAGE", FlagSeverity.HIGH, field="date_of_birth"))

    declared = checks.get(CheckType.DECLARED_MATCH.value)
    if declared and declared["status"] == "not_run" and declared["details"].get("reason") == "DECLARED_IDENTITY_MISSING":
        flags.append(_flag("DECLARED_IDENTITY_MISSING", FlagSeverity.MEDIUM))
    if declared and declared["status"] in ("failed", "inconclusive"):
        for name, entry in declared["details"].get("fields", {}).items():
            if entry["status"] in ("mismatch", "missing"):
                flags.append(_flag("DECLARED_MISMATCH", FlagSeverity.HIGH, field=name, similarity=entry["similarity"]))
            elif entry["status"] == "partial":
                flags.append(_flag("DECLARED_PARTIAL", FlagSeverity.MEDIUM, field=name, similarity=entry["similarity"]))

    if status(CheckType.EXPIRY) == "failed":
        flags.append(_flag("DOCUMENT_EXPIRED", FlagSeverity.HIGH, field="date_of_expiry"))
    elif status(CheckType.EXPIRY) == "not_run":
        flags.append(_flag("EXPIRY_NOT_DETERMINABLE", FlagSeverity.LOW, field="date_of_expiry"))

    if status(CheckType.DUPLICATE_IMAGE) in ("inconclusive", "failed"):
        flags.append(
            _flag(
                "DUPLICATE_DOCUMENT_IMAGE",
                FlagSeverity.HIGH,
                related_cases=details(CheckType.DUPLICATE_IMAGE).get("related_cases", []),
            )
        )
    if status(CheckType.DUPLICATE_IDENTITY) in ("inconclusive", "failed"):
        flags.append(
            _flag(
                "POSSIBLE_DUPLICATE_IDENTITY",
                FlagSeverity.MEDIUM,
                related_cases=details(CheckType.DUPLICATE_IDENTITY).get("related_cases", []),
            )
        )

    if status(CheckType.FACE_MATCH) == "failed":
        flags.append(_flag("FACE_MATCH_FAILED", FlagSeverity.HIGH))
    if status(CheckType.LIVENESS) == "failed":
        flags.append(_flag("LIVENESS_FAILED", FlagSeverity.HIGH))
    return flags


def compute_risk(flags: list[dict]) -> RiskLevel:
    severities = {f["severity"] for f in flags}
    if FlagSeverity.HIGH.value in severities:
        return RiskLevel.HIGH
    if FlagSeverity.MEDIUM.value in severities:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW
