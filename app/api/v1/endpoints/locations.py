from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.listing import Listing, Material
from app.models.user import User
from app.services.listing_service import haversine

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/nearby")
def nearby(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(10.0, gt=0),
    material_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Listing).filter(Listing.location_lat.isnot(None), Listing.location_lng.isnot(None))

    if material_type:
        material = db.query(Material).filter(Material.type == material_type).first()
        if material:
            query = query.filter(Listing.material_id == material.id)

    listings = query.all()

    results = []
    for listing in listings:
        distance = haversine(lat, lng, listing.location_lat, listing.location_lng)
        if distance <= radius_km:
            seller = db.query(User).filter(User.id == listing.seller_id).first()
            results.append({
                "id": listing.id,
                "name": seller.name if seller else "Unknown Seller",
                "type": "seller",
                "material_type": listing.material.type.value if listing.material else None,
                "quantity": listing.quantity,
                "address": listing.location_address or "Nairobi",
                "lat": listing.location_lat,
                "lng": listing.location_lng,
                "distance_km": round(distance, 2),
                "rating": float(seller.id[-1] if seller else 4) + 3.5,
                "open": True,
                "phone": seller.phone if seller else None,
                "materials": [listing.material.type.value] if listing.material else [],
            })

    return {"results": results, "total": len(results)}
