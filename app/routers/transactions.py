import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, Transaction, TransactionType, User
from app.schemas import TransactionCreate, TransactionResponse
from app.routers.auth import get_current_user
from app.email import send_transaction_receipt
from app.services import transactions as transactions_service
from app.exceptions import ProductNotFoundError, InsufficientStockError
from typing import List

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        new_transaction = transactions_service.record_transaction(
            db,
            current_user.id,
            transaction.product_id,
            transaction.type,
            transaction.quantity,
            transaction.note,
        )
    except ProductNotFoundError:
        raise HTTPException(status_code=404, detail="Product not found")
    except InsufficientStockError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough stock. Available: {e.available}"
        )

    try:
        send_transaction_receipt(
            to_email=current_user.email,
            product_name=new_transaction.product.name,
            transaction_type=transaction.type.value,
            quantity=transaction.quantity,
            note=transaction.note
        )
    except Exception:
        logger.warning("Failed to send transaction receipt email", exc_info=True)

    return new_transaction

@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Transaction).join(Product).filter(
        Product.owner_id == current_user.id
    ).order_by(Transaction.created_at.desc()).all()

@router.get("/product/{product_id}", response_model=List[TransactionResponse])
def get_product_transactions(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.owner_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db.query(Transaction).filter(
        Transaction.product_id == product_id
    ).order_by(Transaction.created_at.desc()).all()