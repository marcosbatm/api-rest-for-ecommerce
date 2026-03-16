from datetime import datetime
from pydantic import BaseModel, Field

class Product(BaseModel):
    id: int
    sellerId: int
    title: str
    description: str
    price: float = Field(ge=0.01, description="Price in USD, rounded to 2 decimal places")
    createdAt: datetime
    updatedAt: datetime

class CartItem(BaseModel):
    id: int
    productId: int
    title: str
    unitPrice: float = Field(ge=0.01, description="Snapshot price in USD when item was added to cart, rounded to 2 decimal places")
    addedAt: datetime

class Cart(BaseModel):
    userId: int
    items: list[CartItem]
    totalPrice: float = Field(ge=0, description="Sum of unitPrice of all items, in USD")

