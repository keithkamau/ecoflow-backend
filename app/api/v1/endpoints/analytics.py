from fastapi import APIRouter

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/seller-stats")
def seller_stats():
    return {
        "total_listings": 0,
        "active_listings": 0,
        "total_sales": 0,
        "monthly_earnings": 0,
        "pending_offers": 0,
        "completed_transactions": 0
    }


@router.get("/impact")
def impact():
    return {
        "total_co2_saved_kg": 0,
        "total_landfill_diverted_kg": 0,
        "total_water_saved_liters": 0,
        "total_energy_saved_kwh": 0
    }
