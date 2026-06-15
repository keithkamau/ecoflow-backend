from fastapi import APIRouter

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/")
def list_analytics():
    return {"message": "analytics endpoint working"}
