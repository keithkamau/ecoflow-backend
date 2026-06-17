# app/models/listing.py
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.database import Base


class MaterialType(str, enum.Enum):
    PLASTIC = "plastic"
    METAL = "metal"
    GLASS = "glass"
    E_WASTE = "e_waste"
    PAPER = "paper"
    ORGANIC = "organic"
    MIXED = "mixed"


class ListingStatus(str, enum.Enum):
    ACTIVE = "active"
    MATCHED = "matched"
    COMPLETED = "completed"
    EXPIRED = "expired"


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(MaterialType), unique=True, nullable=False)
    unit = Column(String(20), default="kg")  # kg, pieces, bags
    reference_price = Column(Float, nullable=True)  # KES per unit
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    listings = relationship("Listing", back_populates="material")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, index=True, nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    condition = Column(Text, nullable=True)
    location_lat = Column(Float, nullable=True)
    location_lng = Column(Float, nullable=True)
    location_address = Column(String(255), nullable=True)
    price_expectation = Column(Float, nullable=True)
    preferred_pickup_start = Column(DateTime, nullable=True)
    preferred_pickup_end = Column(DateTime, nullable=True)
    status = Column(Enum(ListingStatus), default=ListingStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    material = relationship("Material", back_populates="listings")
    photos = relationship("ListingPhoto", back_populates="listing", cascade="all, delete-orphan")


class ListingPhoto(Base):
    __tablename__ = "listing_photos"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    photo_url = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    listing = relationship("Listing", back_populates="photos")
