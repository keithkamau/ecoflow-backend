from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.transaction import Transaction, TransactionStatus
from app.models.listing import Listing, ListingStatus
from app.models.user import User


def get_seller_stats(db: Session, user_id: str) -> dict:
    transactions = db.query(Transaction).filter(Transaction.seller_id == user_id)
    completed = transactions.filter(Transaction.status == TransactionStatus.COMPLETED)

    total_kg = completed.with_entities(func.sum(Transaction.final_quantity)).scalar() or 0
    total_earnings = completed.with_entities(func.sum(Transaction.final_price)).scalar() or 0
    tx_count = completed.count()
    active = db.query(Listing).filter(
        Listing.seller_id == user_id,
        Listing.status == ListingStatus.WAITING
    ).count()

    return {
        "total_kg_sold": round(total_kg, 2),
        "total_earnings_kes": round(total_earnings, 2),
        "transactions_completed": tx_count,
        "active_listings": active,
    }


def get_recycler_stats(db: Session, user_id: str) -> dict:
    transactions = db.query(Transaction).filter(Transaction.recycler_id == user_id)
    completed = transactions.filter(Transaction.status == TransactionStatus.COMPLETED)

    total_kg = completed.with_entities(func.sum(Transaction.final_quantity)).scalar() or 0
    total_spent = completed.with_entities(func.sum(Transaction.final_price)).scalar() or 0
    suppliers = completed.with_entities(Transaction.seller_id).distinct().count()
    pickups = completed.count()

    return {
        "total_materials_sourced_kg": round(total_kg, 2),
        "total_spent_kes": round(total_spent, 2),
        "active_suppliers": suppliers,
        "pickups_completed": pickups,
    }


def get_impact_data(db: Session, user_id: str) -> dict:
    seller_tx = db.query(Transaction).filter(
        Transaction.seller_id == user_id,
        Transaction.status == TransactionStatus.COMPLETED
    )
    recycler_tx = db.query(Transaction).filter(
        Transaction.recycler_id == user_id,
        Transaction.status == TransactionStatus.COMPLETED
    )

    kg_sold = seller_tx.with_entities(func.sum(Transaction.final_quantity)).scalar() or 0
    kg_sourced = recycler_tx.with_entities(func.sum(Transaction.final_quantity)).scalar() or 0
    total_kg = kg_sold + kg_sourced
    earnings = seller_tx.with_entities(func.sum(Transaction.final_price)).scalar() or 0

    co2_kg = round(total_kg * 2.0, 2)
    trees = round(total_kg / 11, 1)
    total_users = db.query(User).count()

    all_sellers = (
        db.query(Transaction.seller_id, func.sum(Transaction.final_price).label("total"))
        .filter(Transaction.status == TransactionStatus.COMPLETED)
        .group_by(Transaction.seller_id)
        .order_by(func.sum(Transaction.final_price).desc())
        .all()
    )
    ranking = 1
    for idx, seller in enumerate(all_sellers, start=1):
        if str(seller.seller_id) == user_id:
            ranking = idx
            break

    return {
        "total_kg_recycled": round(total_kg, 2),
        "co2_saved_kg": co2_kg,
        "trees_equivalent": trees,
        "waste_diverted_kg": round(total_kg, 2),
        "total_earnings_kes": round(earnings, 2),
        "ranking": ranking,
        "total_users": total_users,
    }


def get_earnings_trend(db: Session, user_id: str) -> list:
    rows = (
        db.query(
            func.strftime("%Y-%m", Transaction.completed_at).label("month"),
            func.sum(Transaction.final_price).label("earnings"),
            func.sum(Transaction.final_quantity).label("kg"),
        )
        .filter(
            Transaction.seller_id == user_id,
            Transaction.status == TransactionStatus.COMPLETED,
            Transaction.completed_at.isnot(None),
        )
        .group_by(func.strftime("%Y-%m", Transaction.completed_at))
        .order_by("month")
        .all()
    )

    return [
        {"month": r.month, "earnings": round(r.earnings or 0, 2), "kg": round(r.kg or 0, 2)}
        for r in rows
    ]
