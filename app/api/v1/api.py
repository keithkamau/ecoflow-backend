from fastapi import APIRouter
from app.api.v1.endpoints import (
    listings,
    offers,
    payments,
    messages,
    pickups,
    analytics,
    locations,
    auth,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(listings.router, prefix="/listings")
api_router.include_router(offers.router)
api_router.include_router(payments.router)
api_router.include_router(messages.router)
api_router.include_router(pickups.router)
api_router.include_router(analytics.router)
api_router.include_router(locations.router)