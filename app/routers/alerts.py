from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import ProductResponse
from app.routers.auth import get_current_user
from app.services import alerts as alerts_service
from typing import List

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("/low-stock", response_model=List[ProductResponse])
def get_low_stock(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return alerts_service.list_low_stock(db, current_user.id)

@router.get("/expiring", response_model=List[ProductResponse])
def get_expiring(
    days: int = Query(default=7),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return alerts_service.list_expiring(db, current_user.id, days=days)

@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return alerts_service.get_dashboard_summary(db, current_user.id)

@router.get("/analytics/revenue")
def get_revenue_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return alerts_service.get_revenue_analytics(db, current_user.id)