from fastapi import APIRouter

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/")
def list_payments():
    return {"message": "payments endpoint working"}
