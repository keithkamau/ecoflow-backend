from fastapi import APIRouter
from app.api.v1.endpoints import (
    listings,
    analytics,
    locations,
    auth,
    users,
)
from app.routers import (
    offers,
    payments,
    messages,
    transactions,
    notifications,
)
from app.api.v1.endpoints import pickups

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(listings.router)
api_router.include_router(offers.router)
api_router.include_router(payments.router)
api_router.include_router(messages.router)
api_router.include_router(transactions.router)
api_router.include_router(notifications.router)
api_router.include_router(pickups.router)
api_router.include_router(analytics.router)
api_router.include_router(locations.router)
