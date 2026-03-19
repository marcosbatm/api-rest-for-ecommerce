from fastapi import APIRouter, status, Request, Depends
from fastapi.responses import JSONResponse

from src.models.cart import (
    CartItemResponse,
    CartResponse,
    Cart,
    AddProductToCartRequest,
)
from src.models.errors import ErrorResponse

# from src.models.carts import
from src.service.backend import EcommerceBackend

carts_router = APIRouter()


# TODO: Abstraer la dependencia y evitar repetir el get_backend en cada router y endpoint.
def get_backend(request: Request) -> EcommerceBackend:
    return request.app.state.backend


@carts_router.get(
    "/cart/{userId}",
    summary="Get user's cart",
    description="Returns the user's cart with items ordered by addedAt descending, then id descending. An unknown userId returns an empty cart.",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    response_description="User cart retrieved successfully",
)
def read_cart(
    userId: int, backend: EcommerceBackend = Depends(get_backend)
) -> CartResponse:
    cart: Cart = backend.read_cart(userId)
    return CartResponse(data=cart)


@carts_router.delete(
    "/cart/{userId}",
    summary="Wipe a user's cart",
    description="Removes all items from the user's cart. Idempotent - wiping an empty or non-existent cart returns 204.",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Cart wiped successfully",
)
def clear_cart(userId: int, backend: EcommerceBackend = Depends(get_backend)):
    backend.clear_cart(userId)
    return


@carts_router.post(
    "/cart/{userId}/items",
    summary="Add product to user's cart",
    description="Adds a new cart item with a snapshot of the product's current price and title. Each POST creates an independent item (duplicates allowed).",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
    response_description="Product added to cart successfully",
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
            "description": "Product not found error",
            "content": {
                "application/problem+json": {
                    "schema": ErrorResponse.model_json_schema()
                }
            },
        },
    },
)
def add_item_to_cart(
    userId: int,
    request: AddProductToCartRequest,
    backend: EcommerceBackend = Depends(get_backend),
) -> CartItemResponse:
    try:
        new_item = backend.add_item_to_cart_or_fail(userId, request.productId)
        return CartItemResponse(data=new_item)
    except KeyError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                type="about:blank",
                title="Product not found",
                status=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {request.productId} not found",
                instance=f"/cart/{userId}/items",
            ).model_dump(),
            media_type="application/problem+json",
        )


# @carts_router.delete(
#     "/cart/{userId}/items/{cartItemId}",
#     summary="Delete an item from a user's cart",
#     description="Removes a specific item from the user's cart. The item must belong to the specified user.",
# )
# def remove_item_from_cart(userId: int, cartItemId: int):
#     return {
#         "message": "Endpoint to remove an item from the cart for a specific user by userId and cartItemId",
#         "userId": userId,
#         "cartItemId": cartItemId,
#     }
