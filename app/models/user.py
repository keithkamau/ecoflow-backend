import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base, GUID


class User(Base):
    __tablename__ = "users"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone      = Column(String, unique=True, nullable=False, index=True)
    email      = Column(String, unique=True, nullable=True)
    name       = Column(String, nullable=False)
    password   = Column(String, nullable=False)
    role       = Column(Enum("seller", "recycler", "admin", name="user_role"), nullable=False)
    verified   = Column(Boolean, default=False)
    kyc_status = Column(Enum("none", "pending", "verified", "rejected", name="kyc_status"), default="none")
    location   = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    kyc_documents = relationship("KYCDocument", back_populates="user", cascade="all, delete-orphan")


class OTPLog(Base):
    __tablename__ = "otp_logs"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone      = Column(String, nullable=False, index=True)
    otp        = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used       = Column(Boolean, default=False)
    attempts   = Column(Integer, default=0)


class KYCDocument(Base):
    __tablename__ = "kyc_documents"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(GUID(), ForeignKey("users.id"), nullable=False)
    doc_type    = Column(String, nullable=False)
    doc_url     = Column(String, nullable=False)
    status      = Column(Enum("pending", "verified", "rejected", name="doc_status"), default="pending")
    uploaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="kyc_documents")