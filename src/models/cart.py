from datetime import datetime
from pydantic import BaseModel, Field


class BaseCartItem(BaseModel):
    id: int
    productId: int
    title: str
    unitPrice: float = Field(
        ge=0.01,
        description="Snapshot price in USD when item was added to cart, rounded to 2 decimal places",
    )
    addedAt: datetime


class BaseCart(BaseModel):
    userId: int
    items: list[BaseCartItem]
    totalPrice: float = Field(
        minimum=0.0, description="Sum of unitPrice of all items, in USD"
    )


class Cart(BaseCart):
    pass


class CartResponse(BaseModel):
    data: Cart
