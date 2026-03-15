import os
from fastapi import FastAPI
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

class Product(BaseModel):
    id: int
    sellerId: int
    title: str
    description: str
    price: float = Field(ge=0.01, description="Price in USD, rounded to 2 decimal places")
    createdAt: str # TODO: transform to str($date-time)
    updatedAt: str # TODO: transform to str($date-time)

class CartItem(BaseModel):
    id: int
    productId: int
    title: str
    unitPrice: float = Field(ge=0.01, description="Snapshot price in USD when item was added to cart, rounded to 2 decimal places")
    addedAt: str # TODO: transform to str($date-time)

class Cart(BaseModel):
    userId: int
    items: list[CartItem]
    totalPrice: float = Field(ge=0, description="Sum of unitPrice of all items, in USD")

app = FastAPI()

@app.get("/")
def read_root(product: Product, cartItem: CartItem, cart: Cart):
    service_name = os.getenv("SERVICE_NAME", "FastAPI")
    return {"Hello": "World", "From": service_name}

@app.post("/products")
def write_product(product: CreateProductRequest):
    return {"message": "Endpoint to create a new product"}

@app.get("/products")
def read_products():
    return {"message": "Endpoint to read all products"}

@app.get("/products/{id}")
def read_product(id: int):
    return {"message": "Endpoint to read a specific product by id", "id": id}

@app.put("/products/{id}")
def update_product(id: int, product: UpdateProductRequest):
    return {"message": "Endpoint to update a specific product by id", "id": id}

@app.delete("/products/{id}")
def delete_product(id: int):
    return {"message": "Endpoint to delete a specific product by id", "id": id}

@app.get("/cart/{userId}")
def read_cart(userId: int):
    return {"message": "Endpoint to read the cart for a specific user by userId", "userId": userId}

@app.delete("/cart/{userId}")
def clear_cart(userId: int):
    return {"message": "Endpoint to clear the cart for a specific user by userId", "userId": userId}

@app.post("/cart/{userId}/items")
def add_item_to_cart(userId: int, item: AddCartRequest):
    return {"message": "Endpoint to add an item to the cart for a specific user by userId", "userId": userId}

@app.delete("/cart/{userId}/items/{cartItemId}")
def remove_item_from_cart(userId: int, cartItemId: int):
    return {"message": "Endpoint to remove an item from the cart for a specific user by userId and cartItemId", "userId": userId, "cartItemId": cartItemId}
