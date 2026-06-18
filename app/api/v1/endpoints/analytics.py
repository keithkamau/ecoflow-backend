from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.models.transaction import Transaction, TransactionStatus
from app.models.listing import Listing
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/global-stats")
def global_stats(db: Session = Depends(get_db)):
    total_kg = db.query(func.sum(Transaction.final_quantity)).filter(
        Transaction.status.in_([TransactionStatus.PICKUP_COMPLETED, TransactionStatus.COMPLETED])
    ).scalar() or 0
    total_tx = db.query(Transaction).filter(
        Transaction.status.in_([TransactionStatus.PICKUP_COMPLETED, TransactionStatus.COMPLETED])
    ).count()
    total_members = db.query(User).count()
    co2_saved = round(total_kg * 2.0, 2)
    return {
        "total_kg_recycled": round(total_kg, 2),
        "total_transactions": total_tx,
        "total_members": total_members,
        "co2_saved_kg": co2_saved,
    }


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
