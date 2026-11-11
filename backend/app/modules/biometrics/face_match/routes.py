from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def face_match_status() -> dict[str, str]:
    return {"module": "face_match", "status": "initialized"}
