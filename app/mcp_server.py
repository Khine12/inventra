import os
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

from app.database import SessionLocal
from app.exceptions import InsufficientStockError, ProductNotFoundError
from app.models import Product, Transaction, TransactionType, User
from app.services import alerts as alerts_service
from app.services import products as products_service
from app.services import transactions as transactions_service


def _resolve_owner_id() -> int:
    email = os.getenv("INVENTRA_OWNER_EMAIL")
    if not email:
        raise RuntimeError(
            "INVENTRA_OWNER_EMAIL is not set. Set it to the email of the "
            "Inventra user this MCP server should act on behalf of."
        )
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise RuntimeError(
                f"No Inventra user found with email '{email}' "
                "(from INVENTRA_OWNER_EMAIL). Check the env var or register this user first."
            )
        return user.id
    finally:
        db.close()


OWNER_ID = _resolve_owner_id()

mcp = FastMCP("Inventra")


def _serialize_product(product: Product) -> Dict[str, Any]:
    return {
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "quantity": product.quantity,
        "price": product.price,
        "cost_price": product.cost_price,
        "low_stock_threshold": product.low_stock_threshold,
        "expiry_date": product.expiry_date.isoformat() if product.expiry_date else None,
        "created_at": product.created_at.isoformat() if product.created_at else None,
    }


def _serialize_transaction(transaction: Transaction, product_name: str) -> Dict[str, Any]:
    return {
        "id": transaction.id,
        "product_id": transaction.product_id,
        "product_name": product_name,
        "type": transaction.type.value,
        "quantity": transaction.quantity,
        "note": transaction.note,
        "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
    }


@mcp.tool()
def lookup_stock(product_id: Optional[int] = None) -> dict:
    """Look up a single product's stock by id, or list all products if product_id is omitted."""
    db = SessionLocal()
    try:
        result = products_service.lookup_stock(db, OWNER_ID, product_id=product_id)
        if isinstance(result, list):
            return {"success": True, "products": [_serialize_product(p) for p in result]}
        return {"success": True, "product": _serialize_product(result)}
    except ProductNotFoundError as e:
        return {"success": False, "error": "product_not_found", "product_id": e.product_id}
    finally:
        db.close()


@mcp.tool()
def record_transaction(
    product_id: int, type: str, quantity: int, note: Optional[str] = None
) -> dict:
    """Record a sale or restock for a product. Sales are refused if they would drive stock below zero."""
    db = SessionLocal()
    try:
        try:
            txn_type = TransactionType(type)
        except ValueError:
            return {
                "success": False,
                "error": "invalid_type",
                "message": f"type must be 'sale' or 'restock', got '{type}'",
            }

        transaction = transactions_service.record_transaction(
            db, OWNER_ID, product_id, txn_type, quantity, note
        )
        serialized = _serialize_transaction(transaction, transaction.product.name)
        return {"success": True, "transaction": serialized}
    except ProductNotFoundError as e:
        return {"success": False, "error": "product_not_found", "product_id": e.product_id}
    except InsufficientStockError as e:
        return {
            "success": False,
            "error": "insufficient_stock",
            "product_id": e.product_id,
            "available": e.available,
            "requested": e.requested,
            "message": f"Not enough stock. Available: {e.available}, requested: {e.requested}",
        }
    finally:
        db.close()


@mcp.tool()
def list_low_stock() -> dict:
    """List products at or under their low-stock threshold."""
    db = SessionLocal()
    try:
        products = alerts_service.list_low_stock(db, OWNER_ID)
        return {"success": True, "products": [_serialize_product(p) for p in products]}
    finally:
        db.close()


@mcp.tool()
def list_expiring(days: int = 7) -> dict:
    """List products expiring within the given number of days (default 7)."""
    db = SessionLocal()
    try:
        products = alerts_service.list_expiring(db, OWNER_ID, days=days)
        return {"success": True, "products": [_serialize_product(p) for p in products]}
    finally:
        db.close()


@mcp.tool()
def get_dashboard_summary() -> dict:
    """Get total product count, low-stock count, and expiring-soon count."""
    db = SessionLocal()
    try:
        summary = alerts_service.get_dashboard_summary(db, OWNER_ID)
        return {"success": True, **summary}
    finally:
        db.close()


@mcp.tool()
def get_revenue_analytics() -> dict:
    """Get daily revenue/cost/profit breakdown and totals from recorded sales."""
    db = SessionLocal()
    try:
        analytics = alerts_service.get_revenue_analytics(db, OWNER_ID)
        return {"success": True, **analytics}
    finally:
        db.close()


if __name__ == "__main__":
    mcp.run(transport="stdio")
