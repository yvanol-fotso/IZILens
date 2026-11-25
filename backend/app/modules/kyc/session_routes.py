from fastapi import APIRouter, BackgroundTasks, Depends, File, Header, Request, UploadFile
from sqlalchemy.orm import Session

from app.common.constants import SESSION_HEADER
from app.common.enums import CaseStatus, CheckType
from app.core.config import get_settings
from app.core.database import get_db
from app.core.dependencies import client_ip
from app.core.exceptions import Conflict, Unauthorized, ValidationFailed
from app.core.rate_limit import limiter
from app.modules.kyc import journeys, service, visibility
from app.modules.kyc.models import KycCase
from app.modules.kyc.routes import notify
from app.modules.kyc.schemas import (
    AttemptQuota,
    ConsentRequest,
    DeclaredIdentity,
    DeclaredIdentityRead,
    SessionResult,
    SessionView,
)
from app.modules.kyc.states import EDITABLE_DECLARATION, TERMINAL, UPLOADABLE
from app.shared.i18n import messages as i18n

router = APIRouter(prefix="/kyc/session", tags=["Parcours hébergé"])
FINAL_STATUSES = TERMINAL | {CaseStatus.MANUAL_REVIEW}


def session_case(
    request: Request, token: str | None = Header(None, alias=SESSION_HEADER), db: Session = Depends(get_db)
) -> KycCase:
    """Authentifie la personne par son jeton de session, limité par adresse IP, et limité à un seul dossier."""
    limiter.check(f"session:{client_ip(request)}", 120, 60)
    if not token:
        raise Unauthorized("Jeton de session requis", code="SESSION_REQUIRED")
    return service.case_from_session(db, token)


def _next_action(case: KycCase) -> str:
    declared_needed = CheckType.DECLARED_MATCH.value in case.journey.required_checks and not case.declared_identity
    if case.status == CaseStatus.EXPIRED or case.status in TERMINAL:
        return "done"
    if case.consent is None:
        return "accept_terms"
    if declared_needed:
        return "provide_identity"
    if case.status in UPLOADABLE:
        return "upload_document"
    return "wait"


def _view(db: Session, case: KycCase) -> SessionView:
    lang = i18n.normalize_lang(case.language)
    declared_needed = CheckType.DECLARED_MATCH.value in case.journey.required_checks and not case.declared_identity
    allowed = [
        {
            "document_type": c.document_type,
            "label": c.label_fr if lang == "fr" else c.label_en,
            "sides_required": c.sides_required,
        }
        for c in journeys.supported_documents(db, case.country_code)
        if c.document_type == case.document_type
    ]
    reason = case.status_reason if case.status_reason else case.status.value.upper()
    return SessionView(
        reference=case.reference,
        language=case.language,
        country_code=case.country_code,
        status=case.status,
        status_label=i18n.status_label(case.status.value, lang),
        status_reason=case.status_reason,
        message=i18n.reason_message(reason, lang) or i18n.reason_message(case.status.value.upper(), lang),
        expires_at=case.expires_at,
        consent_required=case.consent is None,
        consent_given=case.consent is not None,
        terms_version=get_settings().terms_version,
        declared_identity_required=declared_needed,
        declared_identity=DeclaredIdentityRead(**case.declared_identity) if case.declared_identity else None,
        documents_allowed=allowed,
        instructions=i18n.INSTRUCTIONS[lang]["steps"],
        attempts={k: AttemptQuota(**v.model_dump()) for k, v in visibility.attempts_summary(case).items()},
        can_upload=case.status in UPLOADABLE,
        can_update_identity=case.status in EDITABLE_DECLARATION,
        next_action=_next_action(case),
    )


@router.get("", response_model=SessionView, summary="État du parcours, consignes localisées et actions possibles")
def get_session(case: KycCase = Depends(session_case), db: Session = Depends(get_db)):
    return _view(db, case)


@router.post("/consent", response_model=SessionView, summary="Accepter les conditions de traitement (preuve horodatée)")
def consent(payload: ConsentRequest, request: Request, case: KycCase = Depends(session_case), db: Session = Depends(get_db)):
    if not payload.accepted:
        raise ValidationFailed("Les conditions doivent être acceptées pour poursuivre", code="CONSENT_REQUIRED")
    service.record_consent(db, case, service.PERSON, payload.terms_version, client_ip(request))
    return _view(db, case)


@router.put("/declared-identity", response_model=SessionView, status_code=202, summary="Renseigner ou corriger son identité")
def declared_identity(
    payload: DeclaredIdentity,
    background_tasks: BackgroundTasks,
    case: KycCase = Depends(session_case),
    db: Session = Depends(get_db),
):
    if case.consent is None:
        raise Conflict("Les conditions doivent d'abord être acceptées", code="CONSENT_REQUIRED")
    attempt = service.update_declared_identity(db, case, service.PERSON, payload.to_storage())
    notify(background_tasks, case.id, attempt.id if attempt else None)
    return _view(db, case)


@router.post(
    "/documents", response_model=SessionView, status_code=202, summary="Téléverser son document (nouvelle tentative si reprise)"
)
def upload(
    background_tasks: BackgroundTasks,
    front: UploadFile = File(...),
    back: UploadFile | None = File(None),
    case: KycCase = Depends(session_case),
    db: Session = Depends(get_db),
):
    if case.consent is None:
        raise Conflict("Les conditions doivent d'abord être acceptées", code="CONSENT_REQUIRED")
    if CheckType.DECLARED_MATCH.value in case.journey.required_checks and not case.declared_identity:
        raise Conflict("Votre identité doit d'abord être renseignée", code="DECLARED_IDENTITY_REQUIRED")
    attempt = service.submit_documents(db, case, service.PERSON, front, back)
    notify(background_tasks, case.id, attempt.id)
    return _view(db, case)


@router.get("/result", response_model=SessionResult, summary="Résultat communicable à la personne")
def result(case: KycCase = Depends(session_case)):
    lang = i18n.normalize_lang(case.language)
    reason = case.status_reason or case.status.value.upper()
    return SessionResult(
        status=case.status,
        status_label=i18n.status_label(case.status.value, lang),
        message=i18n.reason_message(reason, lang) or i18n.reason_message(case.status.value.upper(), lang),
        final=case.status in FINAL_STATUSES,
        scope=visibility.scope_of(case, lang),
    )
