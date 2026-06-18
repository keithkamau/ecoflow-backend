from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/seller-stats")
def seller_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return analytics_service.get_seller_stats(db, str(current_user.id))


@router.get("/recycler-stats")
def recycler_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return analytics_service.get_recycler_stats(db, str(current_user.id))


@router.get("/impact")
def impact_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return analytics_service.get_impact_data(db, str(current_user.id))


@router.get("/earnings-trend")
def earnings_trend(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return analytics_service.get_earnings_trend(db, str(current_user.id))
