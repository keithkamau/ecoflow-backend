from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.models.driver import Driver
from app.schemas.pickup import PickupCreate, PickupUpdate, PickupAssignDriver, PickupResponse, DriverInfo
from app.schemas.driver import DriverCreate, DriverResponse
from app.services import pickup_service
from app.services import driver_service
from app.services.storage_service import storage_service

router = APIRouter(prefix="/pickups", tags=["pickups"])


def _enrich(pickup, db) -> PickupResponse:
    data = PickupResponse.model_validate(pickup)
    if pickup.driver_id:
        driver = db.query(Driver).filter(Driver.id == pickup.driver_id).first()
        if driver:
            data.driver = DriverInfo(
                id=driver.id,
                name=driver.name,
                phone=driver.phone,
                vehicle=driver.vehicle,
                license_plate=driver.license_plate,
            )
    return data


@router.get("/drivers", response_model=List[DriverResponse])
def list_drivers(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return driver_service.get_drivers(db, status)


@router.post("/drivers", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
def create_driver(data: DriverCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return driver_service.create_driver(db, data)


@router.get("/", response_model=List[PickupResponse])
def list_pickups(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pickups, total = pickup_service.get_pickups(db, skip, limit)
    return [_enrich(p, db) for p in pickups]


@router.post("/", response_model=PickupResponse, status_code=status.HTTP_201_CREATED)
def create_pickup(
    data: PickupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pickup = pickup_service.create_pickup(db, data)
    return _enrich(pickup, db)


@router.get("/{pickup_id}", response_model=PickupResponse)
def get_pickup(pickup_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pickup = pickup_service.get_pickup(db, pickup_id)
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found")
    return _enrich(pickup, db)


@router.put("/{pickup_id}", response_model=PickupResponse)
def update_pickup(pickup_id: int, data: PickupUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    updated = pickup_service.update_pickup(db, pickup_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Pickup not found")
    return _enrich(updated, db)


@router.post("/{pickup_id}/assign-driver", response_model=PickupResponse)
def assign_driver(pickup_id: int, data: PickupAssignDriver, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    updated = pickup_service.assign_driver(db, pickup_id, data.driver_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Pickup not found")
    return _enrich(updated, db)


@router.post("/{pickup_id}/proof", response_model=PickupResponse)
async def upload_proof(
    pickup_id: int,
    file: UploadFile = File(...),
    weight: Optional[float] = Form(None),
    signature: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pickup = pickup_service.get_pickup(db, pickup_id)
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found")

    proof_url = await storage_service.upload(file, folder="proofs")
    updated = pickup_service.upload_proof(db, pickup_id, proof_url, weight=weight, signature=signature)
    return _enrich(updated, db)
