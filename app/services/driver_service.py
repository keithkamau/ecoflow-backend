from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.driver import Driver, DriverStatus
from app.schemas.driver import DriverCreate


def create_driver(db: Session, data: DriverCreate) -> Driver:
    driver = Driver(
        name=data.name,
        phone=data.phone,
        vehicle=data.vehicle,
        license_plate=data.license_plate,
    )
    db.add(driver)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(driver)
    return driver


def get_drivers(db: Session, status: Optional[str] = None) -> List[Driver]:
    query = db.query(Driver)
    if status:
        query = query.filter(Driver.status == DriverStatus(status))
    return query.all()


def get_driver(db: Session, driver_id: int) -> Optional[Driver]:
    return db.query(Driver).filter(Driver.id == driver_id).first()
