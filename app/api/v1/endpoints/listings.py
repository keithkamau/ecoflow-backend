from fastapi import APIRouter, Depends
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("/")
def list_listings():
    return {"listings": [], "total": 0}


@router.get("/mine")
def my_listings(user=Depends(get_current_user)):
    return {"listings": [], "total": 0}


@router.get("/{listing_id}")
def get_listing(listing_id: str):
    return {"listing": None}


@router.post("/")
def create_listing(user=Depends(get_current_user)):
    return {"message": "Listing created", "listing_id": "placeholder"}


@router.put("/{listing_id}")
def update_listing(listing_id: str, user=Depends(get_current_user)):
    return {"message": "Listing updated"}


@router.delete("/{listing_id}")
def delete_listing(listing_id: str, user=Depends(get_current_user)):
    return {"message": "Listing deleted"}


@router.get("/inventory")
def inventory(user=Depends(get_current_user)):
    return {"inventory": [], "total": 0}
