from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def liveness_status() -> dict[str, str]:
    return {"module": "liveness", "status": "initialized"}
