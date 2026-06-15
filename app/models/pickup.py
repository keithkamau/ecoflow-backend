from sqlalchemy import Column, String
from app.database import Base, GUID

class Placeholder(Base):
    __tablename__ = "pickups"
    id = Column(GUID(), primary_key=True)
    name = Column(String, nullable=True)
