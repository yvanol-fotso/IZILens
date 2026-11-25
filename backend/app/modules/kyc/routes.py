import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Query, Response, UploadFile
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.common.enums import CaseStatus, UserRole
from app.common.schemas import Page
from app.core.config import get_settings
from app.core.database import get_db
from app.core.dependencies import require_access
from app.core.exceptions import ValidationFailed
from app.core.principal import Principal
from app.core.rate_limit import limiter
from app.modules.billing import service as billing
from app.modules.billing.schemas import UsageLine
from app.modules.kyc import journeys, repository, service, visibility
from app.modules.kyc.journey_schemas import CoverageOverview, CoverageRead, JourneyCreate, JourneyRead, JourneyUpdate
from app.modules.kyc.schemas import (
    ActionRequest,
    AssignRequest,
    CaseCreated,
    CaseDetail,
    CaseSummary,
    DecisionRequest,
    DeclaredIdentity,
    EventRead,
    SessionInfo,
)
from app.modules.webhooks import service as webhooks
from app.shared.i18n import messages as i18n

router = APIRouter(prefix="/kyc", tags=["KYC"])

read_access = require_access(UserRole.ADMIN, UserRole.REVIEWER, UserRole.VIEWER, UserRole.INTEGRATION, module="kyc")
submit_access = require_access(UserRole.ADMIN, UserRole.REVIEWER, UserRole.INTEGRATION, module="kyc")
review_access = require_access(UserRole.ADMIN, UserRole.REVIEWER, module="kyc")
admin_access = require_access(UserRole.ADMIN, module="kyc")
PLATFORM = (UserRole.SUPER_ADMIN, UserRole.PLATFORM_COMPLIANCE)


def parse_declared(
    surname: str | None, given_names: str | None, date_of_birth: str | None, nationality: str | None
) -> dict | None:
    provided = [surname, given_names, date_of_birth]
    if not any(provided):
        return None
    if not all(provided):
        raise ValidationFailed(
            "Nom, prénoms et date de naissance doivent être fournis ensemble", code="DECLARED_IDENTITY_INCOMPLETE"
        )
    try:
        return DeclaredIdentity(
            surname=surname, given_names=given_names, date_of_birth=date_of_birth, nationality=nationality
        ).to_storage()  # type: ignore[arg-type]
    except ValidationError as exc:
        raise ValidationFailed("Identité déclarée invalide", code="DECLARED_IDENTITY_INVALID") from exc


def notify(background_tasks: BackgroundTasks, case_id: uuid.UUID, attempt_id: uuid.UUID | None) -> None:
    if attempt_id:
        background_tasks.add_task(service.run_pipeline, case_id, attempt_id)
    else:
        background_tasks.add_task(webhooks.dispatch_pending)


@router.get("/coverage", response_model=CoverageOverview, summary="Documents réellement pris en charge et lacunes de couverture")
def coverage(
    country_code: str | None = Query(None, min_length=2, max_length=2),
    _: Principal = Depends(read_access),
    db: Session = Depends(get_db),
):
    return CoverageOverview(
        supported=[CoverageRead.model_validate(r) for r in journeys.supported_documents(db, country_code)],
        gaps=journeys.coverage_gaps(db),
    )


@router.get("/journeys", response_model=list[JourneyRead], summary="Parcours disponibles (plateforme et organisation)")
def list_journeys(principal: Principal = Depends(read_access), db: Session = Depends(get_db)):
    return journeys.list_journeys(db, principal.organization_id)


@router.post("/journeys", response_model=JourneyRead, status_code=201, summary="Créer un parcours de l'organisation")
def create_journey(payload: JourneyCreate, principal: Principal = Depends(admin_access), db: Session = Depends(get_db)):
    return journeys.create_journey(db, principal, payload, principal.organization_id)


@router.patch("/journeys/{journey_id}", response_model=JourneyRead, summary="Modifier un parcours de l'organisation")
def update_journey(
    journey_id: uuid.UUID, payload: JourneyUpdate, principal: Principal = Depends(admin_access), db: Session = Depends(get_db)
):
    return journeys.update_journey(db, principal, journey_id, payload, scope=principal.organization_id, platform=False)


@router.post(
    "/cases",
    response_model=CaseCreated,
    status_code=202,
    summary="Créer un dossier KYC (documents optionnels : sinon parcours hébergé)",
)
def create_case(
    background_tasks: BackgroundTasks,
    country_code: str | None = Form(
        None,
        pattern=r"^[A-Za-z]{2}$",
        description="Pays de délivrance (ISO 3166-1) ; déduit du type de document s'il est unique dans la matrice",
    ),
    document_type: str = Form(..., pattern=r"^[a-z0-9_]{2,32}$", description="Type de document, voir GET /kyc/coverage"),
    language: str = Form("fr", pattern=r"^(fr|en)$"),
    reference: str | None = Form(None, max_length=64, description="Référence de votre système (unique)"),
    journey_code: str | None = Form(None, max_length=40),
    declared_surname: str | None = Form(None, max_length=80),
    declared_given_names: str | None = Form(None, max_length=80),
    declared_date_of_birth: str | None = Form(None, description="AAAA-MM-JJ"),
    declared_nationality: str | None = Form(None, max_length=60),
    consent_terms_version: str | None = Form(None, max_length=20, description="Version des conditions présentées à la personne"),
    front: UploadFile | None = File(None, description="Recto (JPEG ou PNG)"),
    back: UploadFile | None = File(None, description="Verso (JPEG ou PNG)"),
    principal: Principal = Depends(submit_access),
    db: Session = Depends(get_db),
):
    limiter.check(f"cases:{principal.organization_id}", get_settings().rate_limit_cases_per_minute, 60)
    params = service.CaseParams(
        reference=reference,
        country_code=journeys.resolve_country(db, country_code, document_type),
        document_type=document_type,
        language=language,
        journey_code=journey_code,
        declared=parse_declared(declared_surname, declared_given_names, declared_date_of_birth, declared_nationality),
        consent={"terms_version": consent_terms_version, "source": "client"} if consent_terms_version else None,
    )
    case, token, attempt = service.create_case(db, principal, params, front, back)
    notify(background_tasks, case.id, attempt.id if attempt else None)
    return CaseCreated(
        **visibility.summarize(case).model_dump(),
        session=SessionInfo(token=token, hosted_url=service.hosted_url(token), expires_at=case.expires_at),
    )


@router.get("/cases", response_model=Page[CaseSummary], summary="Lister les dossiers de l'organisation")
def list_cases(
    status: CaseStatus | None = None,
    reference: str | None = Query(None, max_length=64),
    country_code: str | None = Query(None, min_length=2, max_length=2),
    risk_level: str | None = Query(None, pattern=r"^(low|medium|high)$"),
    search: str | None = Query(None, max_length=64, description="Référence ou début d'identifiant"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    lang: str | None = Query(None, pattern=r"^(fr|en)$"),
    principal: Principal = Depends(read_access),
    db: Session = Depends(get_db),
):
    items, total = repository.list_cases(
        db,
        principal.organization_id,
        page=page,
        page_size=page_size,
        status=status,
        reference=reference,
        country_code=country_code,
        risk_level=risk_level or None,
        search=search or None,
    )
    return Page(items=[visibility.summarize(c, lang) for c in items], total=total, page=page, page_size=page_size)


@router.get("/review-queue", response_model=Page[CaseSummary], summary="Dossiers en revue pour l'équipe cliente")
def review_queue(
    mine: bool = False,
    unassigned: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    lang: str | None = Query(None, pattern=r"^(fr|en)$"),
    principal: Principal = Depends(review_access),
    db: Session = Depends(get_db),
):
    items, total = repository.list_cases(
        db,
        principal.organization_id,
        page=page,
        page_size=page_size,
        oldest_first=True,
        status=CaseStatus.MANUAL_REVIEW,
        review_teams=["client", "either"],
        assigned_to=principal.actor_id if mine else None,
        unassigned=unassigned,
    )
    return Page(items=[visibility.summarize(c, lang) for c in items], total=total, page=page, page_size=page_size)


@router.get(
    "/cases/{case_id}",
    response_model=CaseDetail,
    summary="Détail : champs lus, contrôles, signaux, tentatives, actions autorisées",
)
def get_case(
    case_id: uuid.UUID,
    lang: str | None = Query(None, pattern=r"^(fr|en)$"),
    principal: Principal = Depends(read_access),
    db: Session = Depends(get_db),
):
    case = service.scoped_case(db, principal, case_id)
    service.refresh_expiry(db, case)
    return visibility.detail(case, principal.role, lang)


@router.get("/cases/{case_id}/timeline", response_model=list[EventRead], summary="Historique complet du dossier")
def timeline(case_id: uuid.UUID, principal: Principal = Depends(read_access), db: Session = Depends(get_db)):
    return service.scoped_case(db, principal, case_id).events


@router.put(
    "/cases/{case_id}/declared-identity",
    response_model=CaseDetail,
    status_code=202,
    summary="Renseigner ou corriger l'identité déclarée",
)
def put_declared_identity(
    case_id: uuid.UUID,
    payload: DeclaredIdentity,
    background_tasks: BackgroundTasks,
    principal: Principal = Depends(submit_access),
    db: Session = Depends(get_db),
):
    case = service.scoped_case(db, principal, case_id)
    attempt = service.update_declared_identity(db, case, service.Actor.of(principal), payload.to_storage())
    notify(background_tasks, case.id, attempt.id if attempt else None)
    return visibility.detail(case, principal.role)


@router.post(
    "/cases/{case_id}/documents",
    response_model=CaseDetail,
    status_code=202,
    summary="Déposer ou redéposer les documents (nouvelle tentative)",
)
def upload_documents(
    case_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    front: UploadFile = File(...),
    back: UploadFile | None = File(None),
    principal: Principal = Depends(submit_access),
    db: Session = Depends(get_db),
):
    limiter.check(f"cases:{principal.organization_id}", get_settings().rate_limit_cases_per_minute, 60)
    case = service.scoped_case(db, principal, case_id)
    attempt = service.submit_documents(db, case, service.Actor.of(principal), front, back)
    notify(background_tasks, case.id, attempt.id)
    return visibility.detail(case, principal.role)


@router.post("/cases/{case_id}/session", response_model=SessionInfo, summary="Régénérer le lien du parcours hébergé")
def rotate_session(case_id: uuid.UUID, principal: Principal = Depends(submit_access), db: Session = Depends(get_db)):
    case = service.scoped_case(db, principal, case_id)
    token, url = service.rotate_session(db, principal, case)
    return SessionInfo(token=token, hosted_url=url, expires_at=case.expires_at)


@router.post("/cases/{case_id}/assign", response_model=CaseDetail, summary="Assigner un dossier en revue")
def assign(
    case_id: uuid.UUID,
    payload: AssignRequest,
    background_tasks: BackgroundTasks,
    principal: Principal = Depends(review_access),
    db: Session = Depends(get_db),
):
    case = service.assign_case(db, principal, service.scoped_case(db, principal, case_id), payload.assignee_user_id)
    return visibility.detail(case, principal.role)


@router.post("/cases/{case_id}/decision", response_model=CaseDetail, summary="Valider ou refuser un dossier en revue")
def decide(
    case_id: uuid.UUID,
    payload: DecisionRequest,
    background_tasks: BackgroundTasks,
    principal: Principal = Depends(review_access),
    db: Session = Depends(get_db),
):
    case = service.decide(db, principal, service.scoped_case(db, principal, case_id), payload)
    notify(background_tasks, case.id, None)
    return visibility.detail(case, principal.role)


@router.post("/cases/{case_id}/request-action", response_model=CaseDetail, summary="Demander un complément à la personne")
def request_action(
    case_id: uuid.UUID,
    payload: ActionRequest,
    background_tasks: BackgroundTasks,
    principal: Principal = Depends(review_access),
    db: Session = Depends(get_db),
):
    case = service.request_action(db, principal, service.scoped_case(db, principal, case_id), payload.reason)
    notify(background_tasks, case.id, None)
    return visibility.detail(case, principal.role)


@router.post(
    "/cases/{case_id}/reprocess",
    response_model=CaseDetail,
    status_code=202,
    summary="Relancer le traitement après incident technique",
)
def reprocess(
    case_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    principal: Principal = Depends(review_access),
    db: Session = Depends(get_db),
):
    case = service.scoped_case(db, principal, case_id)
    attempt = service.reprocess_case(db, case, service.Actor.of(principal))
    notify(background_tasks, case.id, attempt.id)
    return visibility.detail(case, principal.role)


@router.get("/cases/{case_id}/documents/{document_id}/content", summary="Image d'un document (accès journalisé)")
def document_content(
    case_id: uuid.UUID, document_id: uuid.UUID, principal: Principal = Depends(review_access), db: Session = Depends(get_db)
):
    content, mime_type = service.read_document(db, principal, service.scoped_case(db, principal, case_id), document_id)
    return Response(
        content, media_type=mime_type, headers={"Cache-Control": "private, no-store", "Content-Disposition": "inline"}
    )


@router.get("/usage", response_model=list[UsageLine], summary="Événements facturables de l'organisation")
def usage(
    start: datetime | None = None,
    end: datetime | None = None,
    principal: Principal = Depends(admin_access),
    db: Session = Depends(get_db),
):
    return billing.usage_summary(db, organization_id=principal.organization_id, start=start, end=end)


@router.get("/stats", summary="Compteurs de dossiers par statut")
def stats(principal: Principal = Depends(read_access), db: Session = Depends(get_db)):
    return repository.status_counts(db, principal.organization_id)


@router.get("/messages", summary="Libellés de statuts et de motifs (FR/EN) pour l'interface")
def messages(_: Principal = Depends(read_access)):
    return {"statuses": i18n.STATUS_LABELS, "reasons": i18n.REASONS, "flags": i18n.FLAGS, "fields": i18n.FIELD_LABELS}
