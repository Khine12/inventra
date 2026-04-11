from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models import TransactionType

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ProductCreate(BaseModel):
    name: str
    sku: str
    quantity: int
    cost_price: float = 0.0
    price: float
    low_stock_threshold: int = 10
    expiry_date: Optional[datetime] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    quantity: int
    cost_price: float
    price: float
    low_stock_threshold: int
    expiry_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class TransactionCreate(BaseModel):
    product_id: int
    type: TransactionType
    quantity: int
    note: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    product_id: int
    type: TransactionType
    quantity: int
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True