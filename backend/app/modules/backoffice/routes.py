import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Response
from sqlalchemy.orm import Session

from app.common.enums import CaseStatus, CheckStatus, CheckType, UserRole
from app.common.schemas import Page
from app.core.database import get_db
from app.core.dependencies import require_access
from app.core.principal import Principal
from app.modules.billing import service as billing
from app.modules.billing.schemas import UsageLine
from app.modules.kyc import journeys, repository, service, visibility
from app.modules.kyc.journey_schemas import (
    CoverageRead,
    CoverageUpdate,
    CoverageUpsert,
    JourneyCreate,
    JourneyRead,
    JourneyUpdate,
)
from app.modules.kyc.routes import notify
from app.modules.kyc.schemas import (
    ActionRequest,
    AssignRequest,
    CaseDetail,
    CaseSummary,
    DecisionRequest,
    EventRead,
    ExternalCheckRequest,
    GrantAttemptsRequest,
    TransitionRequest,
)
from app.modules.webhooks import service as webhooks
from app.modules.webhooks.schemas import DeliveryRead

router = APIRouter(prefix="/admin", tags=["Back-office IZI LENS"])
platform = require_access(UserRole.SUPER_ADMIN, UserRole.PLATFORM_COMPLIANCE, tenant=False)
super_only = require_access(UserRole.SUPER_ADMIN, tenant=False)
LANG = Query(None, pattern=r"^(fr|en)$")


@router.get("/kyc/cases", response_model=Page[CaseSummary], summary="Tous les dossiers, toutes organisations")
def list_cases(
    organization_id: uuid.UUID | None = None,
    status: CaseStatus | None = None,
    country_code: str | None = Query(None, min_length=2, max_length=2),
    reference: str | None = Query(None, max_length=64),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    lang: str | None = LANG,
    _: Principal = Depends(platform),
    db: Session = Depends(get_db),
):
    items, total = repository.list_cases(
        db, organization_id, page=page, page_size=page_size, status=status, country_code=country_code, reference=reference
    )
    return Page(items=[visibility.summarize(c, lang) for c in items], total=total, page=page, page_size=page_size)


@router.get("/kyc/review-queue", response_model=Page[CaseSummary], summary="File de revue de l'équipe conformité IZI LENS")
def review_queue(
    organization_id: uuid.UUID | None = None,
    mine: bool = False,
    unassigned: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    lang: str | None = LANG,
    principal: Principal = Depends(platform),
    db: Session = Depends(get_db),
):
    items, total = repository.list_cases(
        db,
        organization_id,
        page=page,
        page_size=page_size,
        oldest_first=True,
        status=CaseStatus.MANUAL_REVIEW,
        review_teams=["platform", "either"],
        assigned_to=principal.actor_id if mine else None,
        unassigned=unassigned,
    )
    return Page(items=[visibility.summarize(c, lang) for c in items], total=total, page=page, page_size=page_size)


@router.get("/kyc/cases/{case_id}", response_model=CaseDetail, summary="Détail complet d'un dossier")
def get_case(
    case_id: uuid.UUID, lang: str | None = LANG, principal: Principal = Depends(platform), db: Session = Depends(get_db)
):
    return visibility.detail(service.scoped_case(db, principal, case_id), principal.role, lang)


@router.get("/kyc/cases/{case_id}/timeline", response_model=list[EventRead], summary="Historique du dossier")
def timeline(case_id: uuid.UUID, principal: Principal = Depends(platform), db: Session = Depends(get_db)):
    return service.scoped_case(db, principal, case_id).events


@router.get("/kyc/cases/{case_id}/documents/{document_id}/content", summary="Image d'un document (accès journalisé)")
def document_content(
    case_id: uuid.UUID, document_id: uuid.UUID, principal: Principal = Depends(platform), db: Session = Depends(get_db)
):
    content, mime_type = service.read_document(db, principal, service.scoped_case(db, principal, case_id), document_id)
    return Response(
        content, media_type=mime_type, headers={"Cache-Control": "private, no-store", "Content-Disposition": "inline"}
    )


@router.post("/kyc/cases/{case_id}/assign", response_model=CaseDetail, summary="Assigner un dossier à un analyste")
def assign(case_id: uuid.UUID, payload: AssignRequest, principal: Principal = Depends(platform), db: Session = Depends(get_db)):
    case = service.assign_case(db, principal, service.scoped_case(db, principal, case_id), payload.assignee_user_id)
    return visibility.detail(case, principal.role)


@router.post("/kyc/cases/{case_id}/decision", response_model=CaseDetail, summary="Décision de l'équipe conformité IZI LENS")
def decide(
    case_id: uuid.UUID,
    payload: DecisionRequest,
    background_tasks: BackgroundTasks,
    principal: Principal = Depends(platform),
    db: Session = Depends(get_db),
):
    case = service.decide(db, principal, service.scoped_case(db, principal, case_id), payload)
    notify(background_tasks, case.id, None)
    return visibility.detail(case, principal.role)


@router.post("/kyc/cases/{case_id}/request-action", response_model=CaseDetail, summary="Demander un complément")
def request_action(
    case_id: uuid.UUID,
    payload: ActionRequest,
    background_tasks: BackgroundTasks,
    principal: Principal = Depends(platform),
    db: Session = Depends(get_db),
):
    case = service.request_action(db, principal, service.scoped_case(db, principal, case_id), payload.reason)
    notify(background_tasks, case.id, None)
    return visibility.detail(case, principal.role)


@router.post(
    "/kyc/cases/{case_id}/reprocess",
    response_model=CaseDetail,
    status_code=202,
    summary="Relancer un dossier en incident technique",
)
def reprocess(
    case_id: uuid.UUID, background_tasks: BackgroundTasks, principal: Principal = Depends(platform), db: Session = Depends(get_db)
):
    case = service.scoped_case(db, principal, case_id)
    attempt = service.reprocess_case(db, case, service.Actor.of(principal))
    notify(background_tasks, case.id, attempt.id)
    return visibility.detail(case, principal.role)


@router.post(
    "/kyc/cases/{case_id}/transition",
    response_model=CaseDetail,
    summary="Changer le statut (super administrateur, motivé, audité)",
)
def transition(
    case_id: uuid.UUID,
    payload: TransitionRequest,
    background_tasks: BackgroundTasks,
    principal: Principal = Depends(super_only),
    db: Session = Depends(get_db),
):
    case = service.admin_transition(
        db, principal, service.scoped_case(db, principal, case_id), payload.to_status, payload.reason, payload.exception
    )
    notify(background_tasks, case.id, None)
    return visibility.detail(case, principal.role)


@router.post(
    "/kyc/cases/{case_id}/grant-attempts",
    response_model=CaseDetail,
    summary="Accorder des tentatives supplémentaires (exception contrôlée)",
)
def grant_attempts(
    case_id: uuid.UUID,
    payload: GrantAttemptsRequest,
    background_tasks: BackgroundTasks,
    principal: Principal = Depends(platform),
    db: Session = Depends(get_db),
):
    case = service.grant_attempts(
        db, principal, service.scoped_case(db, principal, case_id), payload.kind, payload.extra, payload.reason
    )
    notify(background_tasks, case.id, None)
    return visibility.detail(case, principal.role)


@router.post(
    "/kyc/cases/{case_id}/checks",
    response_model=CaseDetail,
    summary="Enregistrer un résultat biométrique (module 2) et réévaluer",
)
def ingest_check(
    case_id: uuid.UUID,
    payload: ExternalCheckRequest,
    background_tasks: BackgroundTasks,
    principal: Principal = Depends(super_only),
    db: Session = Depends(get_db),
):
    case = service.scoped_case(db, principal, case_id)
    service.record_external_check(
        db,
        case,
        service.Actor.of(principal),
        CheckType(payload.check_type),
        CheckStatus(payload.status),
        payload.details,
        payload.engine,
        payload.version,
    )
    notify(background_tasks, case.id, None)
    return visibility.detail(case, principal.role)


@router.get("/kyc/coverage", response_model=list[CoverageRead], summary="Matrice pays × documents complète")
def coverage(_: Principal = Depends(platform), db: Session = Depends(get_db)):
    return journeys.list_coverage(db)


@router.post("/kyc/coverage", response_model=CoverageRead, status_code=201, summary="Ajouter un document à la matrice")
def add_coverage(payload: CoverageUpsert, principal: Principal = Depends(super_only), db: Session = Depends(get_db)):
    return journeys.upsert_coverage(db, principal, payload)


@router.patch(
    "/kyc/coverage/{coverage_id}",
    response_model=CoverageRead,
    summary="Valider ou désactiver un document (supported, testing, disabled)",
)
def update_coverage(
    coverage_id: uuid.UUID, payload: CoverageUpdate, principal: Principal = Depends(super_only), db: Session = Depends(get_db)
):
    return journeys.update_coverage(db, principal, coverage_id, payload)


class _AdminJourneyCreate(JourneyCreate):
    organization_id: uuid.UUID | None = None


@router.get("/kyc/journeys", response_model=list[JourneyRead], summary="Tous les parcours")
def list_journeys(organization_id: uuid.UUID | None = None, _: Principal = Depends(platform), db: Session = Depends(get_db)):
    return journeys.list_journeys(db, organization_id)


@router.post(
    "/kyc/journeys", response_model=JourneyRead, status_code=201, summary="Créer un parcours plateforme ou pour une organisation"
)
def create_journey(payload: _AdminJourneyCreate, principal: Principal = Depends(super_only), db: Session = Depends(get_db)):
    return journeys.create_journey(db, principal, payload, payload.organization_id)


@router.patch("/kyc/journeys/{journey_id}", response_model=JourneyRead, summary="Modifier un parcours et valider ses paramètres")
def update_journey(
    journey_id: uuid.UUID, payload: JourneyUpdate, principal: Principal = Depends(super_only), db: Session = Depends(get_db)
):
    return journeys.update_journey(db, principal, journey_id, payload, scope=None, platform=True)


@router.get("/kyc/stats", summary="Compteurs de dossiers par statut")
def stats(organization_id: uuid.UUID | None = None, _: Principal = Depends(platform), db: Session = Depends(get_db)):
    return repository.status_counts(db, organization_id)


@router.get("/kyc/usage", response_model=list[UsageLine], summary="Événements facturables, toutes organisations")
def usage(
    organization_id: uuid.UUID | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    _: Principal = Depends(platform),
    db: Session = Depends(get_db),
):
    return billing.usage_summary(db, organization_id=organization_id, start=start, end=end)


@router.post("/maintenance/run", summary="Expire les demandes dues et envoie les notifications en attente")
def run_maintenance(_: Principal = Depends(super_only), db: Session = Depends(get_db)):
    expired = service.expire_due_cases(db)
    from app.modules.notifications.service import dispatch_pending as dispatch_emails

    return {
        "expired_cases": expired,
        **{f"webhooks_{k}": v for k, v in webhooks.dispatch_pending().items()},
        **{f"emails_{k}": v for k, v in dispatch_emails().items()},
    }


@router.post("/webhooks/deliveries/{delivery_id}/retry", response_model=DeliveryRead, summary="Rejouer une livraison de webhook")
def retry_delivery(delivery_id: uuid.UUID, _: Principal = Depends(super_only), db: Session = Depends(get_db)):
    return webhooks.retry_delivery(db, delivery_id)
