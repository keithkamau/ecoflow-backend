# database.py
# This is where we set up our connection to the database
# and create the tools we need to talk to it throughout the app

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# connect to the database using the URL we defined in config
#SQLite for now while we'ew developing, POstgreSQL when we deploy
engine = create_engine(settings.DATABASE_URL)

# This is what we'll use to open and close database sessions 
# Keeping autocommit off so we control when changes actually save
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All our models will inherit from this
# SQLAlchemy uses it to know which classes map to database tables 
Base = declarative_base()

# A simple function thta opens a db session for a request
# and makes sure ut gets closed properly when we're done
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()