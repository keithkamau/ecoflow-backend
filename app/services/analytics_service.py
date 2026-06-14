import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.pickup import Pickup, ProofOfPickup, PickupStatus
from app.models.offer import Transaction
from app.models.listing import Listing
from app.models.user import User

# kg CO2 saved per kg of material recycled (IPCC estimates)
CO2_FACTORS: dict[str, float] = {
    "plastic": 1.5,
    "metal": 2.0,
    "paper": 0.8,
    "glass": 0.3,
    "electronics": 3.5,
    "rubber": 1.2,
    "textile": 1.0,
    "other": 0.7,
}
TREES_CO2_KG_PER_YEAR = 21.0  # avg kg CO2 absorbed by one tree per year


class AnalyticsService:

    @staticmethod
    def get_environmental_impact(db: Session, user_id: Optional[uuid.UUID] = None) -> dict:
        query = db.query(ProofOfPickup)
        proofs = query.all()

        total_weight = 0.0
        total_co2 = 0.0
        breakdown: dict[str, float] = {}

        for proof in proofs:
            mat = proof.material_type or "other"
            factor = CO2_FACTORS.get(mat, CO2_FACTORS["other"])
            total_weight += proof.weight
            co2 = proof.weight * factor
            total_co2 += co2
            breakdown[mat] = round(breakdown.get(mat, 0.0) + proof.weight, 2)

        return {
            "total_weight_kg": round(total_weight, 2),
            "co2_saved_kg": round(total_co2, 2),
            "trees_equivalent": round(total_co2 / TREES_CO2_KG_PER_YEAR, 2),
            "total_pickups_completed": len(proofs),
            "material_breakdown": breakdown,
        }

    @staticmethod
    def get_transaction_analytics(db: Session, days: int = 30) -> dict:
        since = datetime.utcnow() - timedelta(days=days)
        pickups = db.query(Pickup).filter(Pickup.created_at >= since).all()

        counts = {s.value: 0 for s in PickupStatus}
        for p in pickups:
            counts[p.status.value] = counts.get(p.status.value, 0) + 1

        return {
            "total_pickups": len(pickups),
            "completed": counts.get("completed", 0),
            "pending": counts.get("pending", 0),
            "in_progress": counts.get("in_progress", 0),
            "cancelled": counts.get("cancelled", 0),
            "period_days": days,
        }

    @staticmethod
    def get_seller_performance(db: Session, seller_id: Optional[uuid.UUID] = None) -> list[dict]:
        query = db.query(
            Transaction.seller_id,
            func.count(Transaction.id).label("total_transactions"),
            func.sum(Transaction.total_amount).label("total_earnings"),
        ).filter(Transaction.status == "completed")

        if seller_id:
            query = query.filter(Transaction.seller_id == seller_id)

        rows = query.group_by(Transaction.seller_id).all()

        result = []
        for row in rows:
            listing_weights = (
                db.query(func.sum(Listing.weight))
                .join(Transaction, Transaction.listing_id == Listing.id)
                .filter(Transaction.seller_id == row.seller_id, Transaction.status == "completed")
                .scalar()
            ) or 0.0

            total_earnings = float(row.total_earnings or 0)
            total_weight = float(listing_weights)
            result.append({
                "seller_id": str(row.seller_id),
                "total_transactions": row.total_transactions,
                "total_weight_sold": round(total_weight, 2),
                "total_earnings": round(total_earnings, 2),
                "avg_price_per_kg": round(total_earnings / total_weight, 2) if total_weight else 0.0,
            })

        return result

    @staticmethod
    def get_recycler_analytics(db: Session, recycler_id: Optional[uuid.UUID] = None) -> list[dict]:
        query = db.query(
            Transaction.buyer_id,
            func.count(Transaction.id).label("total_purchases"),
            func.sum(Transaction.total_amount).label("total_spent"),
        ).filter(Transaction.status == "completed")

        if recycler_id:
            query = query.filter(Transaction.buyer_id == recycler_id)

        rows = query.group_by(Transaction.buyer_id).all()

        result = []
        for row in rows:
            # Material breakdown for this recycler
            material_rows = (
                db.query(Listing.material_type, func.sum(Listing.weight).label("w"))
                .join(Transaction, Transaction.listing_id == Listing.id)
                .filter(Transaction.buyer_id == row.buyer_id, Transaction.status == "completed")
                .group_by(Listing.material_type)
                .order_by(func.sum(Listing.weight).desc())
                .limit(5)
                .all()
            )
            top_materials = [{"material": r.material_type, "weight_kg": round(float(r.w), 2)} for r in material_rows]
            total_weight = sum(m["weight_kg"] for m in top_materials)

            result.append({
                "recycler_id": str(row.buyer_id),
                "total_purchases": row.total_purchases,
                "total_weight_sourced": round(total_weight, 2),
                "total_spent": round(float(row.total_spent or 0), 2),
                "top_materials": top_materials,
            })

        return result
