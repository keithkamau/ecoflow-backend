import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base
from app.api.v1.api import api_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EcoFlow API",
    version="1.0.0",
    description="Waste management and recycling marketplace API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "EcoFlow API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
