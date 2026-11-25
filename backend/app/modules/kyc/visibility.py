from app.common.enums import PLATFORM_ROLES, CaseStatus, CheckType, UserRole
from app.modules.kyc.models import KycCase
from app.modules.kyc.schemas import (
    AttemptQuota,
    AttemptRead,
    CaseDetail,
    CaseSummary,
    CheckRead,
    DocumentRead,
    ExtractedField,
    FlagRead,
    ScopeRead,
)
from app.modules.kyc.states import UPLOADABLE
from app.shared.i18n import messages as i18n

PERSONAL_DATA_ROLES = frozenset({UserRole.ADMIN, UserRole.REVIEWER, UserRole.INTEGRATION}) | PLATFORM_ROLES
DOCUMENT_ROLES = frozenset({UserRole.ADMIN, UserRole.REVIEWER}) | PLATFORM_ROLES
REVIEW_ROLES = frozenset({UserRole.ADMIN, UserRole.REVIEWER}) | PLATFORM_ROLES
LIMITED_KINDS = ("recapture", "data_correction", "technical_retry")


def mask(value: str | None) -> str | None:
    """Masque une donnée personnelle pour les rôles en lecture seule."""
    if not value:
        return value
    return value[0] + "*" * min(len(value) - 1, 6)


def attempts_summary(case: KycCase) -> dict[str, AttemptQuota]:
    result = {}
    for kind in LIMITED_KINDS:
        used = sum(1 for a in case.attempts if a.kind == kind)
        result[kind] = AttemptQuota(used=used, max=case.journey.max_attempts.get(kind, 0) + case.attempt_grants.get(kind, 0))
    return result


def latest_checks(case: KycCase) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    for check in case.checks:
        latest[check.check_type] = {"status": check.status, "details": check.details or {}, "required": check.is_required}
    return latest


def scope_of(case: KycCase, lang: str) -> ScopeRead:
    checks = latest_checks(case)
    executed = sorted(t for t, c in checks.items() if c["status"] not in ("not_run", "pending"))
    not_run = sorted(set(case.journey.required_checks) - set(executed))
    return ScopeRead(
        executed_checks=executed, not_run_checks=not_run, disclaimer=i18n.SCOPE_DISCLAIMER[i18n.normalize_lang(lang)]
    )


def summarize(case: KycCase, lang: str | None = None) -> CaseSummary:
    lang = i18n.normalize_lang(lang or case.language)
    return CaseSummary(
        id=case.id,
        reference=case.reference,
        country_code=case.country_code,
        document_type=case.document_type,
        language=case.language,
        status=case.status,
        status_label=i18n.status_label(case.status.value, lang),
        status_reason=case.status_reason,
        status_message=i18n.reason_message(case.status_reason, lang),
        risk_level=case.risk_level,
        ocr_confidence=case.ocr_confidence,
        expires_at=case.expires_at,
        created_at=case.created_at,
        processed_at=case.processed_at,
        review_team=case.review_team,
        assigned_to_user_id=case.assigned_to_user_id,
    )


def allowed_actions(case: KycCase, role: UserRole) -> list[str]:
    actions: list[str] = []
    if role in DOCUMENT_ROLES:
        actions.append("view_documents")
    if role in REVIEW_ROLES | {UserRole.INTEGRATION} and case.status in UPLOADABLE:
        actions += ["upload_documents", "update_declared_identity"]
    if role in REVIEW_ROLES:
        if case.status == CaseStatus.MANUAL_REVIEW:
            actions += ["assign", "decide", "request_action"]
        if case.status == CaseStatus.FAILED:
            actions.append("reprocess")
    if role in PLATFORM_ROLES:
        actions.append("grant_attempts")
    if role == UserRole.SUPER_ADMIN:
        actions.append("transition")
    return actions


def detail(case: KycCase, role: UserRole, lang: str | None = None) -> CaseDetail:
    """Projection d'un dossier selon le rôle : les lecteurs seuls voient des données personnelles masquées."""
    lang = i18n.normalize_lang(lang or case.language)
    full = role in PERSONAL_DATA_ROLES
    extracted = None
    if case.extracted_data:
        extracted = {}
        for name, data in case.extracted_data["fields"].items():
            item = dict(data)
            if not full:
                item["value"], item["normalized"] = mask(item["value"]), mask(item["normalized"])
            extracted[name] = ExtractedField(**item)
    declared = case.declared_identity
    if declared and not full:
        declared = {k: (mask(v) if isinstance(v, str) else v) for k, v in declared.items()}
    flags = [
        FlagRead(
            **{k: v for k, v in f.items() if k in FlagRead.model_fields and k != "message"}, message=i18n.flag_message(f, lang)
        )
        for f in case.flags or []
    ]
    current_attempt = {}
    for document in sorted(case.documents, key=lambda d: next((a.number for a in case.attempts if a.id == d.attempt_id), 0)):
        current_attempt[document.side] = document.id
    documents = [
        DocumentRead.model_validate(d).model_copy(update={"is_current": current_attempt.get(d.side) == d.id})
        for d in case.documents
    ]
    base = summarize(case, lang).model_dump()
    return CaseDetail(
        **base,
        journey_code=case.journey.code,
        failure_kind=case.failure_kind,
        flags=flags,
        declared_identity=declared,
        extracted=extracted,
        extracted_data={k: (v.normalized or v.value) for k, v in extracted.items() if (v.normalized or v.value)}
        if extracted
        else None,
        failure_reason=case.status_reason if case.status.value == "failed" else None,
        checks=[
            CheckRead(
                check_type=c.check_type,
                status=c.status,
                is_required=c.is_required,
                details=c.details or {},
                created_at=c.created_at,
            )
            for c in case.checks
        ],
        attempts=[AttemptRead.model_validate(a) for a in case.attempts],
        attempts_summary=attempts_summary(case),
        documents=documents,
        scope=scope_of(case, lang),
        allowed_actions=allowed_actions(case, role),
        decided_by_user_id=case.decided_by_user_id,
        decided_at=case.decided_at,
        decision_reason=case.decision_reason,
    )


def biometric_unsatisfied(case: KycCase) -> list[str]:
    checks = latest_checks(case)
    return [
        t.value
        for t in (CheckType.FACE_MATCH, CheckType.LIVENESS)
        if t.value in case.journey.required_checks and checks.get(t.value, {}).get("status") != "passed"
    ]
