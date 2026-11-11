from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def api_root() -> dict[str, str]:
    return {"message": "IZILens API v1"}
