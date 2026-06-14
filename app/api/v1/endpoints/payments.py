"""Payment endpoints — owned by Member 3."""
from fastapi import APIRouter

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/")
def initiate_payment():
    return {"detail": "Not implemented — Member 3"}
