import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, CurrentUser
from app.schemas.pickup_schemas import (
    EnvironmentalImpactResponse,
    TransactionAnalyticsResponse,
    SellerPerformanceResponse,
    RecyclerAnalyticsResponse,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/impact", response_model=EnvironmentalImpactResponse)
def get_environmental_impact(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Aggregate environmental impact: weight diverted, CO2 saved, tree equivalents."""
    return AnalyticsService.get_environmental_impact(db, user_id=current_user.user_id)


@router.get("/transactions", response_model=TransactionAnalyticsResponse)
def get_transaction_analytics(
    days: int = Query(30, ge=1, le=365, description="Lookback window in days"),
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    """Pickup counts by status over the requested period."""
    return AnalyticsService.get_transaction_analytics(db, days=days)


@router.get("/sellers", response_model=List[SellerPerformanceResponse])
def get_seller_analytics(
    seller_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    """Sales volume, earnings, and avg price per seller."""
    return AnalyticsService.get_seller_performance(db, seller_id=seller_id)


@router.get("/recyclers", response_model=List[RecyclerAnalyticsResponse])
def get_recycler_analytics(
    recycler_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    """Sourcing volume, spend, and material breakdown per recycler."""
    return AnalyticsService.get_recycler_analytics(db, recycler_id=recycler_id)
