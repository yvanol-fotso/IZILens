from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def kyb_status() -> dict[str, str]:
    return {"module": "kyb", "status": "initialized"}
