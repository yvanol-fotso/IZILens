from typing import Any

CHECK_TYPES_REQUIRABLE = (
    "document_quality",
    "document_recognition",
    "ocr_extraction",
    "declared_match",
    "face_match",
    "liveness",
)
ATTEMPT_KINDS_LIMITED = ("recapture", "data_correction", "technical_retry")
DECISION_RULE_KEYS = (
    "declared_mismatch",
    "declared_partial",
    "expired_document",
    "underage",
    "duplicate_image",
    "duplicate_identity",
    "low_confidence",
    "biometric_failure",
)
DECISION_RULE_VALUES = ("manual_review", "not_verified")
THRESHOLD_KEYS = ("ocr_review", "name_match", "name_partial")
BILLING_KEYS = ("case_created", "attempts", "manual_review", "extra_checks")

# Valeurs provisoires : à valider par Kafintech (parameters_validated reste faux tant que ce n'est pas fait).
DEFAULT_JOURNEY: dict[str, Any] = {
    "code": "standard",
    "name": "Parcours KYC standard",
    "is_default": True,
    "required_checks": ["document_quality", "document_recognition", "ocr_extraction", "declared_match"],
    "max_attempts": {"recapture": 3, "data_correction": 2, "technical_retry": 3},
    "expiry_hours": 72,
    "auto_decision_enabled": False,
    "review_team": "either",
    "thresholds": {"ocr_review": 0.90, "name_match": 0.90, "name_partial": 0.75},
    "decision_rules": {
        "declared_mismatch": "manual_review",
        "declared_partial": "manual_review",
        "expired_document": "manual_review",
        "underage": "not_verified",
        "duplicate_image": "manual_review",
        "duplicate_identity": "manual_review",
        "low_confidence": "manual_review",
        "biometric_failure": "manual_review",
    },
    "billing": {"case_created": True, "attempts": False, "manual_review": False, "extra_checks": False},
    "parameters_validated": False,
}

DEFAULT_COVERAGE: list[dict[str, Any]] = [
    {
        "country_code": "CM",
        "document_type": "cni_cm",
        "label_fr": "Carte nationale d'identité (Cameroun)",
        "label_en": "National identity card (Cameroon)",
        "sides_required": ["front"],
        "status": "testing",
        "notes": "Recto lu par PaddleOCR ; à valider sur un jeu de test représentatif avant passage en « supported ».",
    }
]
