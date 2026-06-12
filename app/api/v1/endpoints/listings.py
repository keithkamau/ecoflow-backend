import os
import uuid
# app/api/v1/endpoints/listings.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi import UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.listing import ListingStatus
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

router = APIRouter()


#  Materials 

@router.post("/materials", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
def create_material(material: MaterialCreate, db: Session = Depends(get_db)):
    existing = service.get_material_by_type(db, material.type)
    if existing:
        raise HTTPException(status_code=400, detail="Material type already exists")
    return service.create_material(db, material)


@router.get("/materials", response_model=List[MaterialResponse])
def get_materials(db: Session = Depends(get_db)):
    return service.get_materials(db)


# Listings 

@router.post("/listings", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
def create_listing(listing: ListingCreate, db: Session = Depends(get_db)):
    seller_id = 1
    return service.create_listing(db, listing, seller_id)


@router.get("/listings", response_model=ListingSearchResponse)
def get_listings(
    material_type: Optional[str] = Query(None),
    min_quantity: Optional[float] = Query(None),
    max_quantity: Optional[float] = Query(None),
    status: Optional[str] = Query(None),
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    radius_km: Optional[float] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    filters = ListingSearchFilters(
        material_type=material_type,
        min_quantity=min_quantity,
        max_quantity=max_quantity,
        status=status,
        lat=lat,
        lng=lng,
        radius_km=radius_km,
        date_from=date_from,
        date_to=date_to,
    )
    listings, total = service.get_listings(db, filters, skip, limit)
    return {"total": total, "listings": listings}


@router.get("/listings/search", response_model=ListingSearchResponse)
def search_listings(
    material_type: Optional[str] = Query(None),
    min_quantity: Optional[float] = Query(None),
    max_quantity: Optional[float] = Query(None),
    status: Optional[str] = Query(None),
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    radius_km: Optional[float] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    filters = ListingSearchFilters(
        material_type=material_type,
        min_quantity=min_quantity,
        max_quantity=max_quantity,
        status=status,
        lat=lat,
        lng=lng,
        radius_km=radius_km,
        date_from=date_from,
        date_to=date_to,
    )
    listings, total = service.get_listings(db, filters, skip, limit)
    return {"total": total, "listings": listings}


@router.get("/listings/{listing_id}", response_model=ListingResponse)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = service.get_listing(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.put("/listings/{listing_id}", response_model=ListingResponse)
def update_listing(listing_id: int, listing: ListingUpdate, db: Session = Depends(get_db)):
    updated = service.update_listing(db, listing_id, listing)
    if not updated:
        raise HTTPException(status_code=404, detail="Listing not found")
    return updated


@router.delete("/listings/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    deleted = service.delete_listing(db, listing_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Listing not found")
    return None


# Recycler Inventory 

@router.get("/recyclers/inventory", response_model=InventoryResponse)
def get_recycler_inventory(
    recycler_id: int = Query(..., description="Recycler user ID"),
    db: Session = Depends(get_db),
):
    items = service.get_recycler_inventory(db, recycler_id)
    return {"recycler_id": recycler_id, "items": items}


@router.post("/listings/{listing_id}/photos")
async def upload_listing_photo(
    listing_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    UPLOAD_DIR = "uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    listing = service.get_listing(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    file_ext = os.path.splitext(file.filename)[1]
    file_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    photo_url = f"http://localhost:8000/uploads/{file_name}"
    photo = service.add_listing_photo(db, listing_id, photo_url)
    
    return photo
