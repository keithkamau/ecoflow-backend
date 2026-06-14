from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, CurrentUser
from app.models.user import User
from app.schemas.pickup_schemas import DistanceRequest, DistanceResponse, NearbyUserResponse
from app.utils.geolocation import haversine_distance, bounding_box, adjusted_price, distance_surcharge

router = APIRouter(prefix="/locations", tags=["locations"])


@router.post("/distance", response_model=DistanceResponse)
def calculate_distance(
    data: DistanceRequest,
    _: CurrentUser = Depends(get_current_user),
):
    """Calculate distance in km between two coordinates and the pickup price surcharge."""
    dist = haversine_distance(data.origin_lat, data.origin_lng, data.dest_lat, data.dest_lng)
    surcharge = distance_surcharge(dist)
    return DistanceResponse(
        distance_km=round(dist, 2),
        adjusted_price=round(adjusted_price(data.base_price, dist), 2),
        surcharge=round(surcharge, 2),
    )


@router.get("/nearby", response_model=List[NearbyUserResponse])
def get_nearby(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10.0, ge=0.5, le=100.0),
    role: str = Query("recycler", description="Filter by role: recycler | seller"),
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    """Return users of the given role within radius_km of the provided coordinates."""
    min_lat, max_lat, min_lng, max_lng = bounding_box(lat, lng, radius_km)

    candidates = (
        db.query(User)
        .filter(
            User.role == role,
            User.is_active.is_(True),
            User.latitude.isnot(None),
            User.longitude.isnot(None),
            User.latitude.between(min_lat, max_lat),
            User.longitude.between(min_lng, max_lng),
        )
        .all()
    )

    results = []
    for user in candidates:
        dist = haversine_distance(lat, lng, user.latitude, user.longitude)
        if dist <= radius_km:
            results.append(
                NearbyUserResponse(
                    id=user.id,
                    full_name=user.full_name,
                    role=user.role,
                    latitude=user.latitude,
                    longitude=user.longitude,
                    address=user.address,
                    distance_km=round(dist, 2),
                )
            )

    results.sort(key=lambda u: u.distance_km)
    return results
