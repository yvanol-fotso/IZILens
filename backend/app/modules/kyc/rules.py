from collections.abc import Callable
from dataclasses import dataclass, field

from app.common.enums import CaseStatus, CheckType

TRIGGER_REASONS = {
    "underage": "UNDERAGE",
    "declared_mismatch": "DECLARED_MISMATCH",
    "declared_partial": "DECLARED_PARTIAL",
    "expired_document": "DOCUMENT_EXPIRED",
    "duplicate_image": "DUPLICATE_DOCUMENT_IMAGE",
    "duplicate_identity": "POSSIBLE_DUPLICATE_IDENTITY",
    "low_confidence": "LOW_CONFIDENCE",
    "biometric_failure": "REVIEW_REQUIRED",
}


@dataclass(frozen=True)
class Outcome:
    status: CaseStatus
    reason: str
    triggers: list[str] = field(default_factory=list)


def _status(checks: dict[str, dict], check_type: CheckType) -> str | None:
    return checks.get(check_type.value, {}).get("status")


def evaluate(
    checks: dict[str, dict],
    flags: list[dict],
    *,
    required_checks: list[str],
    decision_rules: dict[str, str],
    auto_decision_enabled: bool,
    can_retry: Callable[[str], bool],
) -> Outcome:
    """Moteur de décision : un résultat ambigu n'est jamais transformé en validation positive (R-07)."""
    if any(c["status"] == "error" for c in checks.values()):
        return Outcome(CaseStatus.FAILED, "TECHNICAL_ERROR")

    action: str | None = None
    ocr_details = checks.get(CheckType.OCR_EXTRACTION.value, {}).get("details", {})
    if _status(checks, CheckType.DOCUMENT_QUALITY) == "failed":
        action = "IMAGE_QUALITY"
    elif _status(checks, CheckType.DOCUMENT_RECOGNITION) == "failed":
        action = "DOCUMENT_NOT_RECOGNIZED"
    elif _status(checks, CheckType.OCR_EXTRACTION) == "failed":
        action = "MISSING_FIELDS" if ocr_details.get("missing") else "INVALID_FIELDS"
    if action:
        if can_retry("recapture"):
            return Outcome(CaseStatus.ACTION_REQUIRED, action)
        return Outcome(CaseStatus.MANUAL_REVIEW, "ATTEMPTS_EXHAUSTED", [action.lower()])
    declared = checks.get(CheckType.DECLARED_MATCH.value, {})
    if (
        CheckType.DECLARED_MATCH.value in required_checks
        and declared.get("status") == "not_run"
        and declared.get("details", {}).get("reason") == "DECLARED_IDENTITY_MISSING"
    ):
        return Outcome(CaseStatus.ACTION_REQUIRED, "DECLARED_IDENTITY_REQUIRED")

    codes = {f["code"] for f in flags}
    triggers: list[str] = []
    if "UNDERAGE" in codes:
        triggers.append("underage")
    if _status(checks, CheckType.DECLARED_MATCH) == "failed":
        triggers.append("declared_mismatch")
    if _status(checks, CheckType.DECLARED_MATCH) == "inconclusive":
        triggers.append("declared_partial")
    if _status(checks, CheckType.EXPIRY) == "failed":
        triggers.append("expired_document")
    if _status(checks, CheckType.DUPLICATE_IMAGE) in ("inconclusive", "failed"):
        triggers.append("duplicate_image")
    if _status(checks, CheckType.DUPLICATE_IDENTITY) in ("inconclusive", "failed"):
        triggers.append("duplicate_identity")
    if _status(checks, CheckType.OCR_EXTRACTION) == "inconclusive":
        triggers.append("low_confidence")
    if any(_status(checks, t) in ("failed", "inconclusive") for t in (CheckType.FACE_MATCH, CheckType.LIVENESS)):
        triggers.append("biometric_failure")

    rejecting = [t for t in triggers if decision_rules.get(t, "manual_review") == "not_verified"]
    if rejecting:
        return Outcome(CaseStatus.NOT_VERIFIED, TRIGGER_REASONS[rejecting[0]], triggers)
    if triggers:
        return Outcome(CaseStatus.MANUAL_REVIEW, TRIGGER_REASONS[triggers[0]], triggers)

    for biometric in (CheckType.FACE_MATCH, CheckType.LIVENESS):
        if biometric.value in required_checks and _status(checks, biometric) in (None, "pending", "not_run"):
            return Outcome(CaseStatus.IN_PROGRESS, f"AWAITING_{biometric.name}")

    if any(_status(checks, CheckType(t)) != "passed" for t in required_checks):
        return Outcome(CaseStatus.MANUAL_REVIEW, "REVIEW_REQUIRED", ["required_check_not_passed"])
    if auto_decision_enabled and not any(f["severity"] == "high" for f in flags):
        return Outcome(CaseStatus.VERIFIED, "VERIFIED_AUTOMATIC")
    return Outcome(CaseStatus.MANUAL_REVIEW, "AUTO_DECISION_DISABLED")
