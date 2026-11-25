"""Catalogue des rôles et de leurs permissions : source unique exposée au back-office (GET /admin/roles)."""

ROLES: dict[str, dict] = {
    "super_admin": {
        "scope": "platform",
        "label": {"fr": "Super administrateur", "en": "Super administrator"},
        "permissions": ["*"],
    },
    "platform_compliance": {
        "scope": "platform",
        "label": {"fr": "Conformité IZI LENS", "en": "IZI LENS compliance"},
        "permissions": [
            "kyc.review",
            "kyc.read_all",
            "kyc.grant_attempts",
            "audit.read",
            "security.read",
            "reports.read",
            "requests.read",
        ],
    },
    "sales_agent": {
        "scope": "platform",
        "label": {"fr": "Commercial", "en": "Sales"},
        "permissions": ["requests.read", "requests.manage", "developers.review"],
    },
    "content_editor": {
        "scope": "platform",
        "label": {"fr": "Éditeur de contenus", "en": "Content editor"},
        "permissions": ["cms.read", "cms.manage"],
    },
    "billing_manager": {
        "scope": "platform",
        "label": {"fr": "Gestionnaire de facturation", "en": "Billing manager"},
        "permissions": ["billing.read", "billing.manage", "reports.read"],
    },
    "admin": {
        "scope": "tenant",
        "label": {"fr": "Administrateur", "en": "Administrator"},
        "permissions": [
            "cases.read",
            "cases.create",
            "cases.decide",
            "users.manage",
            "api_keys.manage",
            "webhooks.manage",
            "audit.read",
            "billing.read",
            "developers.request",
        ],
    },
    "reviewer": {
        "scope": "tenant",
        "label": {"fr": "Analyste", "en": "Reviewer"},
        "permissions": ["cases.read", "cases.create", "cases.decide"],
    },
    "viewer": {"scope": "tenant", "label": {"fr": "Lecteur", "en": "Viewer"}, "permissions": ["cases.read"]},
    "integration": {
        "scope": "tenant",
        "label": {"fr": "Intégration", "en": "Integration"},
        "permissions": ["cases.read", "cases.create"],
    },
}
