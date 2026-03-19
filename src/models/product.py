from datetime import datetime
from pydantic import BaseModel, Field


class BaseProduct(BaseModel):
    title: str
    description: str
    price: float = Field(ge=0.01)


class CreateProductRequest(BaseProduct):
    sellerId: int


class UpdateProductRequest(BaseProduct):
    pass


class Product(BaseProduct):
    sellerId: int
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
