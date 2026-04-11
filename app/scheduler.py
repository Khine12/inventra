from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Product, User
from app.email import send_low_stock_alert
from datetime import datetime, timedelta

def check_alerts():
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            low_stock = db.query(Product).filter(
                Product.owner_id == user.id,
                Product.quantity <= Product.low_stock_threshold
            ).all()

            expiring = db.query(Product).filter(
                Product.owner_id == user.id,
                Product.expiry_date <= datetime.utcnow() + timedelta(days=7),
                Product.expiry_date != None
            ).all()

            products_to_alert = []

            for p in low_stock:
                products_to_alert.append({
                    "name": p.name,
                    "sku": p.sku,
                    "quantity": p.quantity,
                    "threshold": p.low_stock_threshold,
                    "reason": "Low Stock"
                })

            for p in expiring:
                products_to_alert.append({
                    "name": p.name,
                    "sku": p.sku,
                    "quantity": p.quantity,
                    "threshold": p.low_stock_threshold,
                    "reason": f"Expiring {p.expiry_date.strftime('%Y-%m-%d')}"
                })

            if products_to_alert:
                send_low_stock_alert(
                    to_email=user.email,
                    low_stock_products=products_to_alert
                )
    finally:
        db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(check_alerts, 'cron', hour=8, minute=0)
scheduler.start()