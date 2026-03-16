from pydantic import BaseModel, Field

class CreateProductRequest(BaseModel):
    sellerId: int
    title: str
    description: str
    price: float = Field(ge=0.01)

class UpdateProductRequest(BaseModel):
    title: str
    description: str
    price: float = Field(ge=0.01)

class AddCartRequest(BaseModel):
    productId: int