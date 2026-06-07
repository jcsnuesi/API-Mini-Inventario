from pydantic import BaseModel, ConfigDict, Field, PositiveInt
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId

# Helper: convierte ObjectId a str para respuestas
def oid_str(oid):
    try:
        return str(oid)
    except Exception:
        return oid

class ProductCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sku: str
    name: str
    category: Optional[str] = None
    price: float = Field(gt=0, description="Price must be greater than 0")
    stock: int = Field(default=0, ge=0, description="Stock must be >= 0")

class ProductUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)

class MovementCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: str
    type: Literal["in", "out"]
    qty: PositiveInt

class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str = Field(...)
    sku: str
    name: str
    category: Optional[str] = None
    price: float
    stock: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None