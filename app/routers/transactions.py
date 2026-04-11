from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, Transaction, TransactionType, User
from app.schemas import TransactionCreate, TransactionResponse
from app.routers.auth import get_current_user
from app.email import send_transaction_receipt
from typing import List

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.id == transaction.product_id,
        Product.owner_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if transaction.type == TransactionType.sale:
        if product.quantity < transaction.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock. Available: {product.quantity}"
            )
        product.quantity -= transaction.quantity

    elif transaction.type == TransactionType.restock:
        product.quantity += transaction.quantity

    new_transaction = Transaction(
        product_id=transaction.product_id,
        type=transaction.type,
        quantity=transaction.quantity,
        note=transaction.note
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    send_transaction_receipt(
        to_email=current_user.email,
        product_name=product.name,
        transaction_type=transaction.type.value,
        quantity=transaction.quantity,
        note=transaction.note
    )

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