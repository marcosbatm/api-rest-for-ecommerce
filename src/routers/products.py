from fastapi import APIRouter, status, Request, Depends
from fastapi.exceptions import RequestValidationError

from src.models.errors import ErrorResponse
from src.models.product import (
    CreateProductRequest,
    CreateProductResponse,
    GetProductsResponse,
)
from src.service.backend import EcommerceBackend

products_router = APIRouter()
# products_router = APIRouter(prefix="/products", tags=["products"])


def get_backend(request: Request) -> EcommerceBackend:
    return request.app.state.backend


@products_router.post(
    "/products",
    response_model=CreateProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    response_description="Product created successfully",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad request error",
            "content": {
                "application/problem+json": {
                    "schema": ErrorResponse.model_json_schema()
                }
            },
        }
    },
)
def write_product(
    productRequest: CreateProductRequest,
    backend: EcommerceBackend = Depends(get_backend),
) -> CreateProductResponse:
    if productRequest.sellerId < 0:
        raise RequestValidationError(
            [
                {
                    "loc": ["body", "sellerId"],
                    "msg": "sellerId must be a nonnegative integer",
                    "type": "value_error",
                }
            ]
        )
    product = backend.create_product(productRequest)
    if not product:
        raise RequestValidationError(
            [
                {
                    "loc": ["body"],
                    "msg": "Failed to create product",
                    "type": "value_error",
                }
            ]
        )
    return CreateProductResponse(data=product)


@products_router.get(
    "/products",
    summary="Retrieve all products",
    description="Returns all products ordered by id ascending",
    response_model=GetProductsResponse,
    status_code=status.HTTP_200_OK,
)
def read_products(
    backend: EcommerceBackend = Depends(get_backend),
) -> GetProductsResponse:
    return backend.read_products()


# @products_router.get("/products/{id}", summary="Retrieve a product by ID")
# def read_product(id: int):
#     return {"message": "Endpoint to read a specific product by id", "id": id}


# @products_router.put(
#     "/products/{id}",
#     summary="Full update of a product by ID",
#     description="Replaces all mutable fields of a product. All fields in the request body are required.",
# )
# def update_product(id: int, product: UpdateProductRequest):
#     return {"message": "Endpoint to update a specific product by id", "id": id}


# @products_router.delete("/products/{id}", summary="Delete a product by ID")
# def delete_product(id: int):
#     return {"message": "Endpoint to delete a specific product by id", "id": id}
