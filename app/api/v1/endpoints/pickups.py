import uuid
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, require_role, CurrentUser
from app.schemas.pickup_schemas import (
    PickupCreate,
    PickupUpdate,
    PickupResponse,
    DriverCreate,
    DriverUpdate,
    DriverResponse,
    ProofOfPickupCreate,
    ProofOfPickupResponse,
)
from app.services.pickup_service import PickupService

router = APIRouter(tags=["pickups"])


# ── Pickups ───────────────────────────────────────────────────────────────────

@router.post("/pickups", response_model=PickupResponse, status_code=201)
def schedule_pickup(
    data: PickupCreate,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return PickupService.create_pickup(db, data)


@router.get("/pickups", response_model=List[PickupResponse])
def list_pickups(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return PickupService.list_pickups(db, skip=skip, limit=limit)


@router.get("/pickups/{pickup_id}", response_model=PickupResponse)
def get_pickup(
    pickup_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return PickupService.get_pickup(db, pickup_id)


@router.put("/pickups/{pickup_id}", response_model=PickupResponse)
def update_pickup(
    pickup_id: uuid.UUID,
    data: PickupUpdate,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return PickupService.update_pickup(db, pickup_id, data)


@router.post("/pickups/{pickup_id}/proof", response_model=ProofOfPickupResponse, status_code=201)
def upload_proof(
    pickup_id: uuid.UUID,
    data: ProofOfPickupCreate,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return PickupService.upload_proof(db, pickup_id, data)


# ── Drivers ───────────────────────────────────────────────────────────────────

@router.post("/drivers", response_model=DriverResponse, status_code=201)
def create_driver(
    data: DriverCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("recycler", "admin")),
):
    return PickupService.create_driver(db, data, current_user.user_id)


@router.get("/drivers", response_model=List[DriverResponse])
def get_drivers(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("recycler", "admin")),
):
    return PickupService.get_available_drivers(db, current_user.user_id)


@router.put("/drivers/{driver_id}", response_model=DriverResponse)
def update_driver(
    driver_id: uuid.UUID,
    data: DriverUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("recycler", "admin")),
):
    return PickupService.update_driver(db, driver_id, data, current_user.user_id)
