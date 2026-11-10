from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def kyc_status() -> dict[str, str]:
    return {"module": "kyc", "status": "initialized"}
