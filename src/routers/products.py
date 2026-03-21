import logging

from fastapi import APIRouter, status, Request, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.models.errors import ErrorResponse
from src.models.product import (
    CreateProductRequest,
    ProductResponse,
    GetProductsResponse,
    UpdateProductRequest,
)
from src.service.backend import EcommerceBackend

products_router = APIRouter()
# products_router = APIRouter(prefix="/products", tags=["products"])
logger = logging.getLogger(__name__)


def get_backend(request: Request) -> EcommerceBackend:
    return request.app.state.backend


@products_router.post(
    "/products",
    response_model=ProductResponse,
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
) -> ProductResponse:
    logger.info("POST /products sellerId=%s", productRequest.sellerId)
    if productRequest.sellerId < 0:
        logger.warning(
            "Rejected product creation: invalid sellerId=%s", productRequest.sellerId
        )
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
        logger.warning(
            "Failed to create product for sellerId=%s", productRequest.sellerId
        )
        raise RequestValidationError(
            [
                {
                    "loc": ["body"],
                    "msg": "Failed to create product",
                    "type": "value_error",
                }
            ]
        )
    logger.info("Product created id=%s", product.id)
    return ProductResponse(data=product)


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
    logger.debug("GET /products")
    return backend.read_products()


@products_router.get(
    "/products/{id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a product by ID",
    response_description="Product retrieved successfully",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Product not found",
            "content": {
                "application/problem+json": {
                    "schema": ErrorResponse.model_json_schema()
                }
            },
        }
    },
)
def read_product(
    id: int,
    backend: EcommerceBackend = Depends(get_backend),
) -> ProductResponse:
    logger.debug("GET /products/%s", id)
    try:
        product = backend.read_product_or_fail(id)
    except KeyError:
        logger.warning("Product not found id=%s", id)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                type="about:blank",
                title="Product not found",
                status=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {id} not found",
                instance=f"/products/{id}",
            ).model_dump(),
            media_type="application/problem+json",
        )
    logger.debug("Product retrieved id=%s", id)
    return ProductResponse(data=product)


@products_router.put(
    "/products/{id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Full update of a product by ID",
    response_description="Product updated successfully",
    description="Replaces all mutable fields of a product. All fields in the request body are required.",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad request error",
            "content": {
                "application/problem+json": {
                    "schema": ErrorResponse.model_json_schema()
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Product not found",
            "content": {
                "application/problem+json": {
                    "schema": ErrorResponse.model_json_schema()
                }
            },
        },
    },
)
def update_product(
    id: int,
    product: UpdateProductRequest,
    backend: EcommerceBackend = Depends(get_backend),
) -> ProductResponse:
    logger.info("PUT /products/%s", id)
    product = backend.update_product(id, product)
    if not product:
        logger.warning("Product not found for update id=%s", id)
        payload = ErrorResponse(
            type="about:blank",
            title="Product not found",
            status=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {id} not found",
            instance=f"/products/{id}",
        ).model_dump()

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=payload,
            media_type="application/problem+json",
        )
    logger.info("Product updated id=%s", id)
    return ProductResponse(data=product)


@products_router.delete(
    "/products/{id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product by ID",
    response_description="Product deleted successfully",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Product not found",
            "content": {
                "application/problem+json": {
                    "schema": ErrorResponse.model_json_schema()
                }
            },
        }
    },
)
def delete_product(id: int, backend: EcommerceBackend = Depends(get_backend)) -> dict:
    logger.info("DELETE /products/%s", id)
    success = backend.delete_product(id)
    if not success:
        logger.warning("Product not found for delete id=%s", id)
        payload = ErrorResponse(
            type="about:blank",
            title="Product not found",
            status=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {id} not found",
            instance=f"/products/{id}",
        ).model_dump()

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=payload,
            media_type="application/problem+json",
        )
    logger.info("Product deleted id=%s", id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
