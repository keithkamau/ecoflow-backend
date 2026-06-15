from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from app.services.transaction_service import (
    get_all_transactions,
    get_transaction_by_id,
    create_transaction,
    update_transaction_status,
)
from app.models.transaction import TransactionStatus

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction_endpoint(transaction: TransactionCreate, db: Session = Depends(get_db)):
    result = create_transaction(
        db,
        offer_id=transaction.offer_id,
        listing_id=transaction.listing_id,
        seller_id=transaction.seller_id,
        recycler_id=transaction.recycler_id,
        agreed_price=transaction.agreed_price,
        final_quantity=transaction.final_quantity,
        final_price=transaction.final_price,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Offer not found")
    if result is False:
        raise HTTPException(status_code=400, detail="Can only create a transaction from an accepted offer")
    return result


@router.get("/", response_model=List[TransactionResponse])
def list_transactions(seller_id: int = None, recycler_id: int = None, db: Session = Depends(get_db)):
    return get_all_transactions(db, seller_id, recycler_id)


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = get_transaction_by_id(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(transaction_id: int, update: TransactionUpdate, db: Session = Depends(get_db)):
    transaction = update_transaction_status(
        db, transaction_id, update.status,
        pickup_notes=update.pickup_notes,
        dispute_reason=update.dispute_reason,
    )
    if not transaction:
        existing = get_transaction_by_id(db, transaction_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Transaction not found")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid state transition from {existing.status.value} to {update.status.value}",
        )
    return transaction
