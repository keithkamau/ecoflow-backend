# app/api/v1/api.py
from fastapi import APIRouter

from app.api.v1.endpoints import listings

api_router = APIRouter()

api_router.include_router(listings.router, prefix="/listings", tags=["listings"])