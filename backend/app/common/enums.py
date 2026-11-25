from enum import StrEnum


class UserRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    PLATFORM_COMPLIANCE = "platform_compliance"  # équipe conformité IZI LENS (back-office)
    CONTENT_EDITOR = "content_editor"  # blog, guides, FAQ
    BILLING_MANAGER = "billing_manager"  # facturation
    SALES_AGENT = "sales_agent"  # demandes commerciales et partenariats
    ADMIN = "admin"
    REVIEWER = "reviewer"
    VIEWER = "viewer"
    INTEGRATION = "integration"  # attribué uniquement aux clés API


PLATFORM_ROLES = frozenset({UserRole.SUPER_ADMIN, UserRole.PLATFORM_COMPLIANCE})
STAFF_ROLES = PLATFORM_ROLES | {UserRole.CONTENT_EDITOR, UserRole.BILLING_MANAGER, UserRole.SALES_AGENT}


class CaseStatus(StrEnum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    ACTION_REQUIRED = "action_required"
    PROCESSING = "processing"
    MANUAL_REVIEW = "manual_review"
    VERIFIED = "verified"
    NOT_VERIFIED = "not_verified"
    FAILED = "failed"
    EXPIRED = "expired"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DocumentSide(StrEnum):
    FRONT = "front"
    BACK = "back"


class Decision(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"


class FlagSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ActorType(StrEnum):
    USER = "user"
    API_KEY = "api_key"
    SYSTEM = "system"
    PERSON = "person"  # la personne vérifiée via le parcours hébergé


class CheckType(StrEnum):
    DOCUMENT_QUALITY = "document_quality"
    DOCUMENT_RECOGNITION = "document_recognition"
    OCR_EXTRACTION = "ocr_extraction"
    DECLARED_MATCH = "declared_match"
    EXPIRY = "expiry"
    DUPLICATE_IMAGE = "duplicate_image"
    DUPLICATE_IDENTITY = "duplicate_identity"
    FACE_MATCH = "face_match"  # module 2 (biométrie)
    LIVENESS = "liveness"  # module 2 (biométrie)


DOCUMENT_CHECKS = (
    CheckType.DOCUMENT_QUALITY,
    CheckType.DOCUMENT_RECOGNITION,
    CheckType.OCR_EXTRACTION,
    CheckType.EXPIRY,
)
BIOMETRIC_CHECKS = (CheckType.FACE_MATCH, CheckType.LIVENESS)


class CheckStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"
    NOT_RUN = "not_run"
    ERROR = "error"
    PENDING = "pending"


class AttemptKind(StrEnum):
    INITIAL = "initial"
    RECAPTURE = "recapture"
    DATA_CORRECTION = "data_correction"
    TECHNICAL_RETRY = "technical_retry"


LIMITED_ATTEMPT_KINDS = (AttemptKind.RECAPTURE, AttemptKind.DATA_CORRECTION, AttemptKind.TECHNICAL_RETRY)


class ReviewTeam(StrEnum):
    CLIENT = "client"
    PLATFORM = "platform"
    EITHER = "either"


class CoverageStatus(StrEnum):
    PLANNED = "planned"
    TESTING = "testing"
    SUPPORTED = "supported"
    DISABLED = "disabled"


class Language(StrEnum):
    FR = "fr"
    EN = "en"


class BillingEventType(StrEnum):
    CASE_CREATED = "case_created"
    ATTEMPT = "attempt"
    EXTRA_CHECK = "extra_check"
    MANUAL_REVIEW = "manual_review"
    TECHNICAL_FAILURE = "technical_failure"


class DeliveryStatus(StrEnum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
