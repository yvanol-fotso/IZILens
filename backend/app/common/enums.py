from enum import StrEnum


class UserRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    REVIEWER = "reviewer"
    VIEWER = "viewer"
    INTEGRATION = "integration"  # attribué uniquement aux clés API


class CaseStatus(StrEnum):
    PROCESSING = "processing"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DocumentSide(StrEnum):
    FRONT = "front"
    BACK = "back"


class DocumentType(StrEnum):
    CNI_CM = "cni_cm"


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
