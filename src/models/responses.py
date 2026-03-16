from pydantic import BaseModel
from src.models.ecommerce import Product

class ErrorResponse(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str

class CreateProductResponse(BaseModel):
    data: Product

class GetProductsResponse(BaseModel):
    data: list[Product]
