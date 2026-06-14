import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.pickup import Pickup, Driver, ProofOfPickup, PickupStatus, DriverStatus
from app.schemas.pickup_schemas import PickupCreate, PickupUpdate, DriverCreate, DriverUpdate, ProofOfPickupCreate


class PickupService:

    @staticmethod
    def create_pickup(db: Session, data: PickupCreate) -> Pickup:
        pickup = Pickup(
            transaction_id=data.transaction_id,
            scheduled_time=data.scheduled_time,
            pickup_location=data.pickup_location.model_dump(),
            notes=data.notes,
        )
        db.add(pickup)
        db.commit()
        db.refresh(pickup)
        return pickup

    @staticmethod
    def list_pickups(db: Session, skip: int = 0, limit: int = 20) -> list[Pickup]:
        return db.query(Pickup).order_by(Pickup.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_pickup(db: Session, pickup_id: uuid.UUID) -> Pickup:
        pickup = db.query(Pickup).filter(Pickup.id == pickup_id).first()
        if not pickup:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pickup not found")
        return pickup

    @staticmethod
    def update_pickup(db: Session, pickup_id: uuid.UUID, data: PickupUpdate) -> Pickup:
        pickup = PickupService.get_pickup(db, pickup_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(pickup, field, value)
        pickup.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(pickup)
        return pickup

    @staticmethod
    def upload_proof(db: Session, pickup_id: uuid.UUID, data: ProofOfPickupCreate) -> ProofOfPickup:
        pickup = PickupService.get_pickup(db, pickup_id)
        if pickup.status == PickupStatus.COMPLETED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pickup already completed")
        if db.query(ProofOfPickup).filter(ProofOfPickup.pickup_id == pickup_id).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Proof already uploaded for this pickup")

        proof = ProofOfPickup(
            pickup_id=pickup_id,
            weight=data.weight,
            material_type=data.material_type,
            photos=data.photos,
            driver_signature=data.driver_signature,
            notes=data.notes,
            timestamp=datetime.utcnow(),
        )
        db.add(proof)
        pickup.status = PickupStatus.COMPLETED
        pickup.actual_time = datetime.utcnow()
        pickup.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(proof)
        return proof

    @staticmethod
    def create_driver(db: Session, data: DriverCreate, recycler_id: uuid.UUID) -> Driver:
        if db.query(Driver).filter(Driver.license_plate == data.license_plate).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="License plate already registered",
            )
        driver = Driver(
            recycler_id=recycler_id,
            name=data.name,
            phone=data.phone,
            vehicle=data.vehicle,
            license_plate=data.license_plate,
        )
        db.add(driver)
        db.commit()
        db.refresh(driver)
        return driver

    @staticmethod
    def get_available_drivers(db: Session, recycler_id: uuid.UUID) -> list[Driver]:
        return (
            db.query(Driver)
            .filter(Driver.recycler_id == recycler_id, Driver.status == DriverStatus.AVAILABLE)
            .all()
        )

    @staticmethod
    def update_driver(db: Session, driver_id: uuid.UUID, data: DriverUpdate, recycler_id: uuid.UUID) -> Driver:
        driver = db.query(Driver).filter(Driver.id == driver_id, Driver.recycler_id == recycler_id).first()
        if not driver:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(driver, field, value)
        db.commit()
        db.refresh(driver)
        return driver
