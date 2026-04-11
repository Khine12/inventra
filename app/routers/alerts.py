from app.models import Transaction
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

@router.get("/analytics/revenue")
def get_revenue_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transactions = db.query(Transaction).join(Product).filter(
        Product.owner_id == current_user.id,
        Transaction.type == "sale"
    ).all()

    daily = {}
    for t in transactions:
        date_key = t.created_at.strftime("%Y-%m-%d")
        product = db.query(Product).filter(Product.id == t.product_id).first()
        if product:
            revenue = product.price * t.quantity
            cost = (product.cost_price or 0) * t.quantity
            profit = revenue - cost
            if date_key not in daily:
                daily[date_key] = {"date": date_key, "revenue": 0, "cost": 0, "profit": 0, "sales": 0}
            daily[date_key]["revenue"] += revenue
            daily[date_key]["cost"] += cost
            daily[date_key]["profit"] += profit
            daily[date_key]["sales"] += t.quantity

    result = sorted(daily.values(), key=lambda x: x["date"])
    
    total_revenue = sum(d["revenue"] for d in result)
    total_profit = sum(d["profit"] for d in result)
    total_cost = sum(d["cost"] for d in result)

    return {
        "daily": result,
        "summary": {
            "total_revenue": round(total_revenue, 2),
            "total_cost": round(total_cost, 2),
            "total_profit": round(total_profit, 2),
            "profit_margin": round((total_profit / total_revenue * 100) if total_revenue > 0 else 0, 1)
        }
    }