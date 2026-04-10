from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, User
from app.schemas import ProductResponse
from app.routers.auth import get_current_user
from datetime import datetime, timedelta
from typing import List

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("/low-stock", response_model=List[ProductResponse])
def get_low_stock(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Product).filter(
        Product.owner_id == current_user.id,
        Product.quantity <= Product.low_stock_threshold
    ).all()

@router.get("/expiring", response_model=List[ProductResponse])
def get_expiring(
    days: int = Query(default=7),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cutoff = datetime.utcnow() + timedelta(days=days)
    return db.query(Product).filter(
        Product.owner_id == current_user.id,
        Product.expiry_date <= cutoff,
        Product.expiry_date != None
    ).all()

@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_products = db.query(Product).filter(Product.owner_id == current_user.id).count()
    low_stock = db.query(Product).filter(
        Product.owner_id == current_user.id,
        Product.quantity <= Product.low_stock_threshold
    ).count()
    cutoff = datetime.utcnow() + timedelta(days=7)
    expiring_soon = db.query(Product).filter(
        Product.owner_id == current_user.id,
        Product.expiry_date <= cutoff,
        Product.expiry_date != None
    ).count()
    return {
        "total_products": total_products,
        "low_stock_count": low_stock,
        "expiring_soon_count": expiring_soon
    }