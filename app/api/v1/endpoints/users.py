"""User profile endpoints — owned by Member 1."""
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_me():
    return {"detail": "Not implemented — Member 1"}
