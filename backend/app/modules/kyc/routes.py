import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Query, Response, UploadFile
from sqlalchemy.orm import Session

from app.common.enums import CaseStatus, UserRole
from app.common.schemas import Page
from app.core.config import get_settings
from app.core.database import get_db
from app.core.dependencies import require_access
from app.core.principal import Principal
from app.core.rate_limit import limiter
from app.modules.kyc import repository, service
from app.modules.kyc.schemas import CaseDetail, CaseSummary, DecisionRequest

router = APIRouter(prefix="/kyc", tags=["KYC"])

read_access = require_access(UserRole.ADMIN, UserRole.REVIEWER, UserRole.VIEWER, UserRole.INTEGRATION, module="kyc")
submit_access = require_access(UserRole.ADMIN, UserRole.REVIEWER, UserRole.INTEGRATION, module="kyc")
review_access = require_access(UserRole.ADMIN, UserRole.REVIEWER, module="kyc")


@router.post(
    "/cases",
    response_model=CaseSummary,
    status_code=202,
    summary="Soumettre un dossier KYC (recto obligatoire, verso optionnel)",
)
def create_case(
    background_tasks: BackgroundTasks,
    front: UploadFile = File(..., description="Recto de la CNI (JPEG ou PNG)"),
    back: UploadFile | None = File(None, description="Verso de la CNI (JPEG ou PNG)"),
    reference: str | None = Form(None, max_length=64, description="Référence de votre système (unique)"),
    principal: Principal = Depends(submit_access),
    db: Session = Depends(get_db),
):
    limiter.check(f"cases:{principal.organization_id}", get_settings().rate_limit_cases_per_minute, 60)
    case = service.create_case(db, principal, front=front, back=back, reference=reference)
    background_tasks.add_task(service.process_case, case.id)
    return case


@router.get("/cases", response_model=Page[CaseSummary], summary="Lister les dossiers de l'organisation")
def list_cases(
    status: CaseStatus | None = None,
    reference: str | None = Query(None, max_length=64),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    principal: Principal = Depends(read_access),
    db: Session = Depends(get_db),
):
    items, total = repository.list_cases(
        db,
        principal.organization_id,
        status=status,
        reference=reference,
        page=page,
        page_size=page_size,  # type: ignore[arg-type]
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.get("/cases/{case_id}", response_model=CaseDetail, summary="Détail d'un dossier : champs extraits, signaux de risque")
def get_case(case_id: uuid.UUID, principal: Principal = Depends(read_access), db: Session = Depends(get_db)):
    return service.to_detail(service.get_case(db, principal, case_id))


@router.post("/cases/{case_id}/decision", response_model=CaseDetail, summary="Approuver ou rejeter un dossier en revue")
def decide(
    case_id: uuid.UUID,
    payload: DecisionRequest,
    principal: Principal = Depends(review_access),
    db: Session = Depends(get_db),
):
    return service.to_detail(service.decide(db, principal, case_id, payload))


@router.post(
    "/cases/{case_id}/reprocess", response_model=CaseSummary, status_code=202, summary="Relancer l'OCR d'un dossier en échec"
)
def reprocess(
    case_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    principal: Principal = Depends(review_access),
    db: Session = Depends(get_db),
):
    case = service.reprocess_case(db, principal, case_id)
    background_tasks.add_task(service.process_case, case.id)
    return case


@router.get("/cases/{case_id}/documents/{document_id}/content", summary="Télécharger l'image d'un document (accès journalisé)")
def document_content(
    case_id: uuid.UUID,
    document_id: uuid.UUID,
    principal: Principal = Depends(review_access),
    db: Session = Depends(get_db),
):
    content, mime_type = service.read_document(db, principal, case_id, document_id)
    return Response(
        content, media_type=mime_type, headers={"Cache-Control": "private, no-store", "Content-Disposition": "inline"}
    )
