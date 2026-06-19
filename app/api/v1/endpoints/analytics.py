from fastapi import APIRouter, Depends
from app.middleware.auth_middleware import get_current_user
router = APIRouter(prefix="/analytics", tags=["analytics"])
@router.get("/seller-stats")
def seller_stats(u=Depends(get_current_user)): return {"total_listings":0,"active_listings":0,"total_sales":0,"monthly_earnings":0,"pending_offers":0,"completed_transactions":0}
@router.get("/recycler-stats")
def recycler_stats(u=Depends(get_current_user)): return {"total_purchased_kg":0,"total_spent":0,"processing_count":0,"completed_count":0,"co2_saved_kg":0}
@router.get("/global-stats")
def global_stats(): return {"total_users":0,"total_listings":0,"total_transactions":0,"total_waste_diverted_kg":0,"total_co2_saved_kg":0}
@router.get("/earnings-trend")
def earnings_trend(u=Depends(get_current_user)): return []
@router.get("/impact")
def impact(): return {"total_co2_saved_kg":0,"total_landfill_diverted_kg":0,"total_water_saved_liters":0,"total_energy_saved_kwh":0}
