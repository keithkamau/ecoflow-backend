# Run: python -m migrations.migrate_listing_statuses
# Maps old ListingStatus enum values to new values

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, SessionLocal
from sqlalchemy import text

OLD_TO_NEW = {
    "ACTIVE": "WAITING", "active": "WAITING",
    "MATCHED": "OFFER_ACCEPTED", "matched": "OFFER_ACCEPTED",
    "COMPLETED": "PICKUP_COMPLETE", "completed": "PICKUP_COMPLETE",
    "EXPIRED": "PICKUP_COMPLETE", "expired": "PICKUP_COMPLETE",
    "waiting": "WAITING", "offer_accepted": "OFFER_ACCEPTED",
    "awaiting_pickup": "AWAITING_PICKUP", "pickup_complete": "PICKUP_COMPLETE",
}

def migrate():
    db = SessionLocal()
    try:
        raw = db.execute(text('SELECT id, status FROM listings')).fetchall()
        updated = 0
        for row in raw:
            old = row[1]
            if old in OLD_TO_NEW:
                new = OLD_TO_NEW[old]
                db.execute(text('UPDATE listings SET status = :new WHERE id = :id'), {"new": new, "id": row[0]})
                updated += 1
        db.commit()
        print(f"Migrated {updated} listings")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
