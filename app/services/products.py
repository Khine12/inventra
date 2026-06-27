from typing import List, Optional, Union
from sqlalchemy.orm import Session
from app.models import Product
from app.exceptions import ProductNotFoundError


def lookup_stock(
    db: Session, owner_id: int, product_id: Optional[int] = None
) -> Union[Product, List[Product]]:
    if product_id is None:
        return db.query(Product).filter(Product.owner_id == owner_id).all()

    product = db.query(Product).filter(
        Product.id == product_id, Product.owner_id == owner_id
    ).first()
    if not product:
        raise ProductNotFoundError(product_id)
    return product
