import os
from fastapi import FastAPI
from pydantic import BaseModel, Field
from src.models.requests import CreateProductRequest, UpdateProductRequest, AddCartRequest
from src.models.responses import CreateProductResponse, ErrorResponse, GetProductsResponse

app = FastAPI()

@app.post("/products", summary="Create a new product")
def write_product(product: CreateProductRequest) -> CreateProductResponse:
    return {"message": "Endpoint to create a new product"}

@app.get("/products", summary="Retrieve all products", description="Returns all products ordered by id ascending")
def read_products() -> GetProductsResponse:
    return {"message": "Endpoint to read all products"}

@app.get("/products/{id}", summary="Retrieve a product by ID")
def read_product(id: int):
    return {"message": "Endpoint to read a specific product by id", "id": id}

@app.put("/products/{id}", summary="Full update of a product by ID", description="Replaces all mutable fields of a product. All fields in the request body are required.")
def update_product(id: int, product: UpdateProductRequest):
    return {"message": "Endpoint to update a specific product by id", "id": id}

@app.delete("/products/{id}", summary="Delete a product by ID")
def delete_product(id: int):
    return {"message": "Endpoint to delete a specific product by id", "id": id}

@app.get("/cart/{userId}", summary="Get user's cart", description="Returns the user's cart with items ordered by addedAt descending, then id descending. An unknown userId returns an empty cart.")
def read_cart(userId: int):
    return {"message": "Endpoint to read the cart for a specific user by userId", "userId": userId}

@app.delete("/cart/{userId}", summary="Wipe a user's cart", description="Removes all items from the user's cart. Idempotent - wiping an empty or non-existent cart returns 204.")
def clear_cart(userId: int):
    return {"message": "Endpoint to clear the cart for a specific user by userId", "userId": userId}

@app.post("/cart/{userId}/items", summary="Add product to user's cart", description="Adds a new cart item with a snapshot of the product's current price and title. Each POST creates an independent item (duplicates allowed).")
def add_item_to_cart(userId: int, item: AddCartRequest):
    return {"message": "Endpoint to add an item to the cart for a specific user by userId", "userId": userId}

@app.delete("/cart/{userId}/items/{cartItemId}", summary="Delete an item from a user's cart", description="Removes a specific item from the user's cart. The item must belong to the specified user.")
def remove_item_from_cart(userId: int, cartItemId: int):
    return {"message": "Endpoint to remove an item from the cart for a specific user by userId and cartItemId", "userId": userId, "cartItemId": cartItemId}
