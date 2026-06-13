# app/services/listing_service.py
from typing import List, Optional
from math import radians, cos, sin, asin, sqrt

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.listing import Material, Listing, ListingPhoto, MaterialType, ListingStatus
from app.schemas.listing_schemas import (
    ListingCreate,
    ListingUpdate,
    MaterialCreate,
    ListingSearchFilters,
)


def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on earth (in km)"""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r


def create_material(db: Session, material: MaterialCreate) -> Material:
    db_material = Material(
        type=material.type,
        unit=material.unit,
        reference_price=material.reference_price,
        description=material.description,
    )
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material


def get_materials(db: Session) -> List[Material]:
    return db.query(Material).all()


def get_material_by_type(db: Session, material_type: str) -> Optional[Material]:
    return db.query(Material).filter(Material.type == material_type).first()


def create_listing(db: Session, listing: ListingCreate, seller_id: int) -> Listing:
    db_listing = Listing(
        seller_id=seller_id,
        material_id=listing.material_id,
        quantity=listing.quantity,
        condition=listing.condition,
        location_lat=listing.location_lat,
        location_lng=listing.location_lng,
        location_address=listing.location_address,
        price_expectation=listing.price_expectation,
        preferred_pickup_start=listing.preferred_pickup_start,
        preferred_pickup_end=listing.preferred_pickup_end,
        status=ListingStatus.ACTIVE,
    )
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing


def get_listing(db: Session, listing_id: int) -> Optional[Listing]:
    return db.query(Listing).filter(Listing.id == listing_id).first()


def get_listings(
    db: Session,
    filters: Optional[ListingSearchFilters] = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[List[Listing], int]:
    query = db.query(Listing)

    if filters:
        if filters.material_type:
            material = get_material_by_type(db, filters.material_type)
            if material:
                query = query.filter(Listing.material_id == material.id)

        if filters.min_quantity is not None:
            query = query.filter(Listing.quantity >= filters.min_quantity)
        if filters.max_quantity is not None:
            query = query.filter(Listing.quantity <= filters.max_quantity)
        if filters.status:
            query = query.filter(Listing.status == filters.status)
        if filters.date_from:
            query = query.filter(Listing.created_at >= filters.date_from)
        if filters.date_to:
            query = query.filter(Listing.created_at <= filters.date_to)

    total = query.count()
    listings = query.offset(skip).limit(limit).all()

    # Filter by radius if provided
    if filters and filters.lat is not None and filters.lng is not None and filters.radius_km is not None:
        filtered = []
        for listing in listings:
            if listing.location_lat is not None and listing.location_lng is not None:
                distance = haversine(filters.lat, filters.lng, listing.location_lat, listing.location_lng)
                if distance <= filters.radius_km:
                    filtered.append(listing)
        listings = filtered
        total = len(listings)

    return listings, total


def update_listing(
    db: Session, listing_id: int, listing_update: ListingUpdate
) -> Optional[Listing]:
    db_listing = get_listing(db, listing_id)
    if not db_listing:
        return None

    update_data = listing_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_listing, field, value)

    db.commit()
    db.refresh(db_listing)
    return db_listing


def delete_listing(db: Session, listing_id: int) -> bool:
    db_listing = get_listing(db, listing_id)
    if not db_listing:
        return False

    db.delete(db_listing)
    db.commit()
    return True


def add_listing_photo(db: Session, listing_id: int, photo_url: str) -> ListingPhoto:
    db_photo = ListingPhoto(listing_id=listing_id, photo_url=photo_url)
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo


def get_recycler_inventory(db: Session, recycler_id: int) -> List[dict]:
    results = (
        db.query(
            Material.type.label("material_type"),
            func.sum(Listing.quantity).label("total_quantity"),
            func.count(Listing.id).label("listing_count"),
        )
        .join(Material, Listing.material_id == Material.id)
        .filter(Listing.seller_id == recycler_id)
        .filter(Listing.status == ListingStatus.COMPLETED)
        .group_by(Material.type)
        .all()
    )

    inventory = []
    for row in results:
        inventory.append({
            "material_type": row.material_type,
            "total_quantity": float(row.total_quantity or 0),
            "listing_count": row.listing_count,
        })

    return inventory


def update_listing_status(
    db: Session, listing_id: int, status: str
) -> Optional[Listing]:
    db_listing = get_listing(db, listing_id)
    if not db_listing:
        return None

    db_listing.status = status
    db.commit()
    db.refresh(db_listing)
    return db_listing


def accept_offer(
    db: Session, listing_id: int, accepted_quantity: float
) -> Optional[Listing]:
    db_listing = get_listing(db, listing_id)
    if not db_listing:
        return None
    
    if db_listing.status != ListingStatus.ACTIVE:
        return None
    
    if accepted_quantity > db_listing.quantity:
        return None
    
    db_listing.quantity -= accepted_quantity
    
    if db_listing.quantity <= 0:
        db_listing.status = ListingStatus.COMPLETED
    else:
        db_listing.status = ListingStatus.MATCHED
    
    db.commit()
    db.refresh(db_listing)
    return db_listing
