import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.api.v1.api import api_router

from app.models.listing import Material, MaterialType
from app.routers.websocket import router as websocket_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EcoFlow API",
    version="1.0.0",
    description="Waste management and recycling marketplace API",
    redirect_slashes=False,
)


@app.on_event("startup")
def seed_materials():
    db: Session = SessionLocal()
    try:
        if db.query(Material).count() == 0:
            defaults = [
                ("plastic", MaterialType.PLASTIC, "kg", 50),
                ("metal", MaterialType.METAL, "kg", 80),
                ("glass", MaterialType.GLASS, "kg", 30),
                ("paper", MaterialType.PAPER, "kg", 25),
                ("e-waste", MaterialType.E_WASTE, "kg", 120),
                ("organic", MaterialType.ORGANIC, "kg", 15),
                ("mixed", MaterialType.MIXED, "kg", 40),
            ]
            for name, mat_type, unit, price in defaults:
                db.add(Material(type=mat_type, unit=unit, reference_price=price))
            db.commit()
    finally:
        db.close()

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(api_router, prefix="/api/v1")
app.include_router(websocket_router)


@app.get("/")
def root():
    return {"message": "EcoFlow API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

