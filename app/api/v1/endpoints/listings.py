"""Listing endpoints — owned by Member 2."""
from fastapi import APIRouter

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("/")
def list_listings():
    return {"detail": "Not implemented — Member 2"}


@router.post("/")
def create_listing():
    return {"detail": "Not implemented — Member 2"}
