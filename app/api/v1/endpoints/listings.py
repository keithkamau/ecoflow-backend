from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi import UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, require_role
from app.models.listing import ListingStatus
from app.models.user import User
from app.schemas.listing_schemas import (
    ListingCreate,
    ListingUpdate,
    ListingResponse,
    MaterialCreate,
    MaterialResponse,
    ListingSearchFilters,
    ListingSearchResponse,
    InventoryResponse,
)
from app.services import listing_service as service
from app.services.storage_service import storage_service

router = APIRouter()


#  Materials 

@router.post("/materials", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
def create_material(material: MaterialCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    existing = service.get_material_by_type(db, material.type)
    if existing:
        raise HTTPException(status_code=400, detail="Material type already exists")
    return service.create_material(db, material)


@router.get("/materials", response_model=List[MaterialResponse])
def get_materials(db: Session = Depends(get_db)):
    return service.get_materials(db)


# Listings 

@router.post("/", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
def create_listing(
    listing: ListingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_listing(db, listing, str(current_user.id))


@router.get("/mine", response_model=ListingSearchResponse)
def get_my_listings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    listings, total = service.get_user_listings(db, str(current_user.id), skip, limit)
    return {"total": total, "listings": listings}


@router.get("/", response_model=ListingSearchResponse)
def get_listings(
    material_type: Optional[str] = Query(None),
    quantity: Optional[float] = Query(None, gt=0),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    filters = ListingSearchFilters(
        material_type=material_type,
        quantity=quantity,
        status=status,
        date_from=date_from,
        date_to=date_to,
    )
    listings, total = service.get_listings(db, filters, skip, limit)
    return {"total": total, "listings": listings}


@router.get("/search", response_model=ListingSearchResponse)
def search_listings(
    material_type: Optional[str] = Query(None),
    quantity: Optional[float] = Query(None, gt=0),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    filters = ListingSearchFilters(
        material_type=material_type,
        quantity=quantity,
        status=status,
        date_from=date_from,
        date_to=date_to,
    )
    listings, total = service.get_listings(db, filters, skip, limit)
    return {"total": total, "listings": listings}


@router.get("/{listing_id}", response_model=ListingResponse)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = service.get_listing(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.put("/{listing_id}", response_model=ListingResponse)
def update_listing(listing_id: int, listing: ListingUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    updated = service.update_listing(db, listing_id, listing)
    if not updated:
        raise HTTPException(status_code=404, detail="Listing not found")
    return updated


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_listing(listing_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deleted = service.delete_listing(db, listing_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Listing not found")
    return None


# Recycler Inventory

@router.get("/recyclers/inventory", response_model=InventoryResponse)
def get_recycler_inventory(
    recycler_id: str = Query(..., description="Recycler user ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = service.get_recycler_inventory(db, recycler_id)
    return {"recycler_id": recycler_id, "items": items}


@router.post("/{listing_id}/photos")
async def upload_listing_photo(
    listing_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    listing = service.get_listing(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    photo_url = await storage_service.upload(file, folder="uploads")
    photo = service.add_listing_photo(db, listing_id, photo_url)
    return photo
