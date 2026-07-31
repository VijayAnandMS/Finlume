from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from app.database import get_db
from app.models.models import User, Transaction
from app.schemas.schemas import TransactionCreate, TransactionOut
from app.routes.auth import get_current_user
import uuid

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

@router.post("/", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(
    tx_in: TransactionCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    new_tx = Transaction(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        transaction_date=tx_in.transaction_date,
        transaction_type=tx_in.transaction_type,
        category=tx_in.category,
        subcategory=tx_in.subcategory,
        amount=tx_in.amount,
        currency=tx_in.currency,
        merchant=tx_in.merchant,
        payment_method=tx_in.payment_method,
        description=tx_in.description,
        notes=tx_in.notes,
        tags=tx_in.tags,
        receipt_image=tx_in.receipt_image
    )
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)
    return new_tx

@router.get("/", response_model=List[TransactionOut])
def get_transactions(
    # Filtering
    search: Optional[str] = None,
    type: Optional[str] = None,           # 'income' or 'expense'
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    merchant: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    payment_method: Optional[str] = None,
    tags: Optional[str] = None,
    # Sorting
    sort_by: Optional[str] = "date",      # 'date' or 'amount'
    sort_order: Optional[str] = "desc",   # 'asc' or 'desc'
    # Pagination
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    
    if search:
        query = query.filter(
            or_(
                Transaction.description.ilike(f"%{search}%"),
                Transaction.merchant.ilike(f"%{search}%"),
                Transaction.notes.ilike(f"%{search}%")
            )
        )
        
    if type:
        query = query.filter(Transaction.transaction_type == type)
    if category:
        query = query.filter(Transaction.category == category)
    if subcategory:
        query = query.filter(Transaction.subcategory == subcategory)
    if merchant:
        query = query.filter(Transaction.merchant.ilike(f"%{merchant}%"))
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)
    if payment_method:
        query = query.filter(Transaction.payment_method == payment_method)
    if tags:
        query = query.filter(Transaction.tags.ilike(f"%{tags}%"))
        
    # Apply Sorting
    if sort_by == "amount":
        if sort_order == "asc":
            query = query.order_by(asc(Transaction.amount))
        else:
            query = query.order_by(desc(Transaction.amount))
    else:  # default to 'date'
        if sort_order == "asc":
            query = query.order_by(asc(Transaction.transaction_date))
        else:
            query = query.order_by(desc(Transaction.transaction_date))
            
    transactions = query.offset(skip).limit(limit).all()
    return transactions

@router.get("/{tx_id}", response_model=TransactionOut)
def get_transaction(
    tx_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    tx = db.query(Transaction).filter(Transaction.id == tx_id, Transaction.user_id == current_user.id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx

@router.put("/{tx_id}", response_model=TransactionOut)
def update_transaction(
    tx_id: str, 
    tx_in: TransactionCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    tx = db.query(Transaction).filter(Transaction.id == tx_id, Transaction.user_id == current_user.id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    tx.transaction_date = tx_in.transaction_date
    tx.transaction_type = tx_in.transaction_type
    tx.category = tx_in.category
    tx.subcategory = tx_in.subcategory
    tx.amount = tx_in.amount
    tx.currency = tx_in.currency
    tx.merchant = tx_in.merchant
    tx.payment_method = tx_in.payment_method
    tx.description = tx_in.description
    tx.notes = tx_in.notes
    tx.tags = tx_in.tags
    tx.receipt_image = tx_in.receipt_image
    
    db.commit()
    db.refresh(tx)
    return tx

@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    tx_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    tx = db.query(Transaction).filter(Transaction.id == tx_id, Transaction.user_id == current_user.id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    db.delete(tx)
    db.commit()
    return {"status": "success", "message": "Transaction deleted"}
