from datetime import datetime
from pydantic import BaseModel, Field


class BaseProduct(BaseModel):
    sellerId: int
    title: str
    description: str
    price: float = Field(ge=0.01)


class CreateProductRequest(BaseProduct):
    pass


class Product(BaseProduct):
    id: int
    price: float = Field(
        ge=0.01, description="Price in USD, rounded to 2 decimal places"
    )
    createdAt: datetime
    updatedAt: datetime


class ProductResponse(BaseModel):
    data: Product


class GetProductsResponse(BaseModel):
    data: list[Product]
