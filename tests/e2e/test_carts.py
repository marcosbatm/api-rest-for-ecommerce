from httpx import Response
from fastapi.testclient import TestClient
from src.models.product import Product, ProductResponse
from src.models.cart import Cart, CartItem, CartResponse, CartItemResponse
from src.models.errors import ErrorResponse


def _assert_problem_response(
    response: Response, expected_title: str, expected_status: int
) -> None:
    """Helper to assert that a response is a problem+json with the expected title and status."""
    assert response.status_code == expected_status
    assert response.headers["content-type"] == "application/problem+json"

    body: ErrorResponse = ErrorResponse.model_validate(response.json(), extra="forbid")

    assert body.type == "about:blank"
    assert body.title == expected_title
    assert body.status == expected_status
    assert body.detail is not None
    assert body.instance is not None


def _create_product(
    client: TestClient, *, seller_id: int, title: str, price: float
) -> Product:
    """Create a product through the API and return the created resource payload."""
    payload = {
        "sellerId": seller_id,
        "title": title,
        "description": f"Description for {title}",
        "price": price,
    }
    response = client.post("/products", json=payload)

    body: ProductResponse = ProductResponse.model_validate(
        response.json(), extra="forbid"
    )

    return Product.model_validate(body.data, extra="forbid")


def _assert_cart_response(
    response: Response, expected_cart: Cart, expected_status: int
) -> None:
    """Helper to assert that a response is a CartResponse with the expected fields."""
    assert response.status_code == expected_status
    assert response.headers["content-type"] == "application/json"

    body: CartResponse = CartResponse.model_validate(response.json(), extra="forbid")
    cart: Cart = body.data

    assert cart == expected_cart


def test_get_cart_of_nonexistent_user_response(client: TestClient) -> None:
    """Check that retrieving a cart for a non-existent user returns 200 with an empty cart."""
    response = client.get("/cart/678")

    assert response.status_code == 200
    body: CartResponse = CartResponse.model_validate(response.json(), extra="forbid")
    cart: Cart = Cart.model_validate(body.data, extra="forbid")
    assert cart.userId == 678
    assert len(cart.items) == 0
    assert cart.totalPrice == 0.0


def test_wipe_cart_of_nonexistent_user_response(client: TestClient) -> None:
    """Check that wiping a cart for a non-existent user returns 204."""
    response = client.delete("/cart/67891011")

    assert response.status_code == 204


# POST /cart/{userId}/items
def test_add_item_invalid_to_cart_response(client: TestClient) -> None:
    """Check that adding a non-existent product to cart returns 404 with the expected schema."""
    payload = {"productId": 987654321}
    response = client.post("/cart/123/items", json=payload)

    _assert_problem_response(
        response, expected_title="Product not found", expected_status=404
    )


def test_add_item_with_missing_fields_to_cart_response(client: TestClient) -> None:
    """Check that adding a product to cart with missing fields returns 422 with the expected schema."""
    payload = {}  # Missing productId
    response = client.post("/cart/123/items", json=payload)

    _assert_problem_response(
        response, expected_title="Bad Request", expected_status=400
    )


def test_add_item_with_invalid_fields_to_cart_response(client: TestClient) -> None:
    """Check that adding a product to cart with invalid fields returns 422 with the expected schema."""
    payload = {"productId": "not-an-integer"}  # productId should be an integer
    response = client.post("/cart/123/items", json=payload)

    _assert_problem_response(
        response, expected_title="Bad Request", expected_status=400
    )


def test_add_item_with_negative_id_to_cart_response(client: TestClient) -> None:
    """Check that adding a product to cart with a negative productId returns 422 with the expected schema."""
    payload = {"productId": -5}  # productId should be a positive integer
    response = client.post("/cart/123/items", json=payload)

    _assert_problem_response(
        response, expected_title="Bad Request", expected_status=400
    )


def test_add_item_to_cart_response(client: TestClient) -> None:
    """Check that adding a valid product to cart returns 201 with the expected cart."""
    # First, create a product to add to the cart
    created_product: Product = _create_product(
        client, seller_id=1, title="Test Product", price=19.99
    )

    # Now, add that product to the cart
    cart_user_id = 123
    response = client.post(
        f"/cart/{cart_user_id}/items", json={"productId": created_product.id}
    )

    assert response.status_code == 201
    assert response.headers["content-type"] == "application/json"

    body: CartItemResponse = CartItemResponse.model_validate(
        response.json(), extra="forbid"
    )
    cart: CartItem = body.data
    assert cart.id > 0
    assert cart.productId == created_product.id
    assert cart.title == created_product.title
    assert cart.unitPrice == round(created_product.price, 2)
    assert cart.addedAt is not None


def test_add_many_items_to_cart_response(client: TestClient) -> None:
    """Check that adding multiple products to cart returns 201 with the expected cart."""
    # First, create multiple products to add to the cart
    created_product_1: Product = _create_product(
        client, seller_id=1, title="Test Product 1", price=10.00
    )
    created_product_2: Product = _create_product(
        client, seller_id=1, title="Test Product 2", price=15.50
    )

    # Now, add both products to the cart
    cart_user_id = 456
    response_1 = client.post(
        f"/cart/{cart_user_id}/items", json={"productId": created_product_1.id}
    )
    response_2 = client.post(
        f"/cart/{cart_user_id}/items", json={"productId": created_product_2.id}
    )

    assert response_1.status_code == 201
    assert response_2.status_code == 201

    body_1: CartItemResponse = CartItemResponse.model_validate(
        response_1.json(), extra="forbid"
    )
    body_2: CartItemResponse = CartItemResponse.model_validate(
        response_2.json(), extra="forbid"
    )
    cart_1: CartItem = body_1.data
    cart_2: CartItem = body_2.data

    assert cart_1.productId == created_product_1.id
    assert cart_1.title == created_product_1.title
    assert cart_1.unitPrice == round(created_product_1.price, 2)
    assert cart_1.addedAt is not None
    assert cart_2.productId == created_product_2.id
    assert cart_2.title == created_product_2.title
    assert cart_2.unitPrice == round(created_product_2.price, 2)
    assert cart_2.addedAt is not None
    assert cart_1.id != cart_2.id
    assert cart_1.addedAt < cart_2.addedAt


def test_get_cart_of_user_with_items_response(client: TestClient) -> None:
    """Check that retrieving a cart for an existing user returns 200 with the expected schema."""
    # First, create a product and add it to the cart
    created_product: Product = _create_product(
        client, seller_id=1, title="Test Product", price=19.99
    )
    cart_user_id = 123
    post_response: Response = client.post(
        f"/cart/{cart_user_id}/items", json={"productId": created_product.id}
    )

    cartItemResponse: CartItemResponse = CartItemResponse.model_validate(
        post_response.json(), extra="forbid"
    )

    # Now, retrieve the cart and check the response
    response = client.get(f"/cart/{cart_user_id}")

    expected_cart = Cart(
        userId=cart_user_id,
        items=[cartItemResponse.data],
        totalPrice=round(created_product.price, 2),
    )

    _assert_cart_response(response, expected_cart=expected_cart, expected_status=200)


def test_cart_of_user_with_items_is_persistent(client: TestClient) -> None:
    """Check that a cart with items is persistent across multiple retrievals."""
    # First, create a product and add it to the cart
    created_product: Product = _create_product(
        client, seller_id=1, title="Test Product", price=19.99
    )
    cart_user_id = 123
    post_response: Response = client.post(
        f"/cart/{cart_user_id}/items", json={"productId": created_product.id}
    )

    cartItemResponse: CartItemResponse = CartItemResponse.model_validate(
        post_response.json(), extra="forbid"
    )

    # Now, retrieve the cart and check that the item is still there
    expected_cart = Cart(
        userId=cart_user_id,
        items=[cartItemResponse.data],
        totalPrice=round(created_product.price, 2),
    )

    response = client.get(f"/cart/{cart_user_id}")
    _assert_cart_response(response, expected_cart=expected_cart, expected_status=200)


def test_product_update_does_not_affect_cart_item_snapshot(client: TestClient) -> None:
    """Check that updating a product's price does not affect the unitPrice of existing cart items."""
    # First, create a product and add it to the cart
    created_product: Product = _create_product(
        client, seller_id=1, title="Test Product", price=19.99
    )
    cart_user_id = 123
    post_response: Response = client.post(
        f"/cart/{cart_user_id}/items", json={"productId": created_product.id}
    )

    cartItemResponse: CartItemResponse = CartItemResponse.model_validate(
        post_response.json(), extra="forbid"
    )

    # Now, update the product's price
    updated_price = 29.99
    update_payload = {
        "title": created_product.title,
        "description": created_product.description,
        "price": updated_price,
    }
    client.put(f"/products/{created_product.id}", json=update_payload)

    # Finally, retrieve the cart and check that the unitPrice of the cart item has not changed
    expected_cart = Cart(
        userId=cart_user_id,
        items=[cartItemResponse.data],
        totalPrice=round(
            created_product.price, 2
        ),  # Should still reflect original price
    )

    response = client.get(f"/cart/{cart_user_id}")
    _assert_cart_response(response, expected_cart=expected_cart, expected_status=200)


# DELETE /cart/{userId}
def test_wipe_cart_of_user_with_one_item(client: TestClient) -> None:
    """Check that wiping a cart for an existing user returns 204 and empties the cart."""
    # First, create a product and add it to the cart
    created_product: Product = _create_product(
        client, seller_id=1, title="Test Product", price=19.99
    )
    cart_user_id = 123
    client.post(f"/cart/{cart_user_id}/items", json={"productId": created_product.id})

    # Now, wipe the cart
    response = client.delete(f"/cart/{cart_user_id}")

    assert response.status_code == 204

    # Finally, retrieve the cart and check that it's empty
    get_response = client.get(f"/cart/{cart_user_id}")
    expected_cart = Cart(userId=cart_user_id, items=[], totalPrice=0.0)
    _assert_cart_response(
        get_response, expected_cart=expected_cart, expected_status=200
    )


def test_wipe_cart_of_user_with_many_items(client: TestClient) -> None:
    """Check that wiping a cart for an existing user with many items returns 204 and empties the cart."""
    # First, create multiple products and add them to the cart
    created_product_1: Product = _create_product(
        client, seller_id=1, title="Test Product 1", price=10.00
    )
    created_product_2: Product = _create_product(
        client, seller_id=1, title="Test Product 2", price=15.50
    )

    cart_user_id = 456
    client.post(f"/cart/{cart_user_id}/items", json={"productId": created_product_1.id})
    client.post(f"/cart/{cart_user_id}/items", json={"productId": created_product_2.id})

    # Now, wipe the cart
    response = client.delete(f"/cart/{cart_user_id}")

    assert response.status_code == 204

    # Finally, retrieve the cart and check that it's empty
    get_response = client.get(f"/cart/{cart_user_id}")
    expected_cart = Cart(userId=cart_user_id, items=[], totalPrice=0.0)
    _assert_cart_response(
        get_response, expected_cart=expected_cart, expected_status=200
    )


def test_remove_item_from_empty_cart_response(client: TestClient) -> None:
    """Check that removing a non-existent item from cart returns 404 with the expected schema."""
    response = client.delete("/cart/123/items/999")

    _assert_problem_response(
        response, expected_title="Cart item not found", expected_status=404
    )


def test_remove_item_not_in_cart_response(client: TestClient) -> None:
    """Check that removing an item that is not in the cart returns 404 with the expected schema."""
    # First, create a product but do not add it to the cart
    created_product: Product = _create_product(
        client, seller_id=1, title="Test Product", price=19.99
    )
    item_not_in_cart = 100000

    # Now, attempt to remove that product from the cart
    response = client.delete(f"/cart/123/items/{item_not_in_cart}")

    _assert_problem_response(
        response, expected_title="Cart item not found", expected_status=404
    )


def test_remove_item_from_cart_response(client: TestClient) -> None:
    """Check that removing an existing item from cart returns 204 and updates the cart."""
    # First, create a product and add it to the cart
    created_product: Product = _create_product(
        client, seller_id=1, title="Test Product", price=19.99
    )
    cart_user_id = 123
    post_response: Response = client.post(
        f"/cart/{cart_user_id}/items", json={"productId": created_product.id}
    )

    cartItemResponse: CartItemResponse = CartItemResponse.model_validate(
        post_response.json(), extra="forbid"
    )

    # Now, remove that item from the cart
    response = client.delete(f"/cart/{cart_user_id}/items/{cartItemResponse.data.id}")

    assert response.status_code == 204

    # Finally, retrieve the cart and check that it's empty
    get_response = client.get(f"/cart/{cart_user_id}")
    expected_cart = Cart(userId=cart_user_id, items=[], totalPrice=0.0)
    _assert_cart_response(
        get_response, expected_cart=expected_cart, expected_status=200
    )
