from fastapi import APIRouter, status, Request, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.models.cart import CartResponse, Cart
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
    cart = backend.read_cart(userId)
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


# @carts_router.post(
#     "/cart/{userId}/items",
#     summary="Add product to user's cart",
#     description="Adds a new cart item with a snapshot of the product's current price and title. Each POST creates an independent item (duplicates allowed).",
# )
# def add_item_to_cart(userId: int, item: AddCartRequest):
#     return {
#         "message": "Endpoint to add an item to the cart for a specific user by userId",
#         "userId": userId,
#     }


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
