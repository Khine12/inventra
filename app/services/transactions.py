from typing import Optional
from sqlalchemy.orm import Session
from app.models import Product, Transaction, TransactionType
from app.exceptions import ProductNotFoundError, InsufficientStockError


def record_transaction(
    db: Session,
    owner_id: int,
    product_id: int,
    type: TransactionType,
    quantity: int,
    note: Optional[str] = None,
) -> Transaction:
    product = db.query(Product).filter(
        Product.id == product_id, Product.owner_id == owner_id
    ).first()

    if not product:
        raise ProductNotFoundError(product_id)

    if type == TransactionType.sale:
        if product.quantity < quantity:
            raise InsufficientStockError(
                product_id, available=product.quantity, requested=quantity
            )
        product.quantity -= quantity
    elif type == TransactionType.restock:
        product.quantity += quantity

    new_transaction = Transaction(
        product_id=product_id,
        type=type,
        quantity=quantity,
        note=note,
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction
