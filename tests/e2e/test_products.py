from decimal import Decimal, ROUND_HALF_UP

from httpx import Response
from fastapi.testclient import TestClient
from src.models.product import Product, ProductResponse, GetProductsResponse
from src.models.errors import ErrorResponse


def round_to_two_decimals_half_up(value: float) -> float:
    """Round a value to 2 decimal places using ROUND_HALF_UP rounding mode."""
    return float(
        Decimal(str(value)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    )


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


def _assert_product_response(
    response: Response, payload: dict, expected_status: int
) -> None:
    """Helper to assert that a response is a ProductResponse with the expected fields."""
    assert response.status_code == expected_status
    assert response.headers["content-type"] == "application/json"

    body: ProductResponse = ProductResponse.model_validate(
        response.json(), extra="forbid"
    )

    product: Product = Product.model_validate(body.data, extra="forbid")
    assert isinstance(product.id, int)
    assert product.sellerId == payload["sellerId"]
    assert product.title == payload["title"]
    assert product.description == payload["description"]
    assert isinstance(product.price, (float))
    assert product.price == round_to_two_decimals_half_up(payload["price"])


def _create_and_assert_product(
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

    # Should split this in several tests in the future.
    _assert_product_response(response, payload, expected_status=201)

    body: ProductResponse = ProductResponse.model_validate(
        response.json(), extra="forbid"
    )

    return Product.model_validate(body.data, extra="forbid")


# POST /products
def test_create_valid_product_response(client: TestClient) -> None:
    """Validate that creating a product returns 201 and expected data."""
    payload = {
        "sellerId": 101,
        "title": "Keyboard",
        "description": "Mechanical keyboard",
        "price": 149,
    }

    response = client.post("/products", json=payload)
    _assert_product_response(response, payload, expected_status=201)


def test_create_valid_product_rounds_price_to_2_decimals(client: TestClient) -> None:
    """Validate that product creation rounds price to 2 decimals."""
    payload = {
        "sellerId": 102,
        "title": "Monitor",
        "description": "4K monitor",
        "price": 13.456789,
    }

    response = client.post("/products", json=payload)

    body = response.json()["data"]
    assert body["price"] == round_to_two_decimals_half_up(payload["price"])


def test_create_product_with_negative_seller_id_response(client: TestClient) -> None:
    """Validate that creating a product with a negative sellerId returns 400 with the expected error."""
    payload = {
        "sellerId": -1,
        "title": "Invalid Product",
        "description": "Product with negative seller",
        "price": 50.0,
    }

    response = client.post("/products", json=payload)

    _assert_problem_response(
        response, expected_title="Bad Request", expected_status=400
    )


def test_create_invalid_product_response(client: TestClient) -> None:
    """Validate that creating a product with missing required fields returns 400 with the expected error."""
    payload = {
        "sellerId": 10,
        "description": "Missing title and price",
    }

    response = client.post("/products", json=payload)

    _assert_problem_response(
        response, expected_title="Bad Request", expected_status=400
    )


# GET /products
def test_get_products_with_no_products_response(client: TestClient) -> None:
    """Validate that listing products when none exist returns 200 with an empty list."""
    response = client.get("/products")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    body: GetProductsResponse = GetProductsResponse.model_validate(
        response.json(), extra="forbid"
    )

    assert isinstance(body.data, list)
    assert len(body.data) == 0


def test_get_products_returns_all_products_by_ascending_id(client: TestClient) -> None:
    """Verify that listing returns all products sorted by ascending id."""
    first: Product = _create_and_assert_product(
        client, seller_id=1, title="Mouse", price=10.0
    )
    second: Product = _create_and_assert_product(
        client, seller_id=2, title="Keyboard", price=149.99
    )
    third: Product = _create_and_assert_product(
        client, seller_id=3, title="Speaker", price=89.99
    )

    response = client.get("/products")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    body: GetProductsResponse = GetProductsResponse.model_validate(
        response.json(), extra="forbid"
    )

    assert [product.id for product in body.data] == [
        first.id,
        second.id,
        third.id,
    ]


# GET /products/{id}
def test_get_nonexistent_product_by_id_response(client: TestClient) -> None:
    """Check that fetching a non-existent product returns 404 with the expected schema."""
    response = client.get("/products/999999")

    _assert_problem_response(
        response, expected_title="Product not found", expected_status=404
    )


def test_get_existing_product_by_id_response(client: TestClient) -> None:
    """Check that an existing product can be retrieved by id with status 200."""
    created: Product = _create_and_assert_product(
        client, seller_id=9, title="Headset", price=79.99
    )

    response = client.get(f"/products/{created.id}")

    assert response.status_code == 200

    body: ProductResponse = ProductResponse.model_validate(
        response.json(), extra="forbid"
    )

    product: Product = Product.model_validate(body.data, extra="forbid")
    assert created == product


# PUT /products/{id}
def test_update_nonexistent_product_response(client: TestClient) -> None:
    """Validate that updating a non-existent product returns 404 with the expected schema."""
    update_payload = {
        "title": "Updated Title",
        "description": "Updated Description",
        "price": 100.0,
    }

    response = client.put("/products/999999", json=update_payload)

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"

    _assert_problem_response(
        response, expected_title="Product not found", expected_status=404
    )


def test_update_existing_product_with_invalid_data_response(client: TestClient) -> None:
    """Validate that updating an existing product with invalid data returns 400 with the expected schema."""
    created: Product = _create_and_assert_product(
        client, seller_id=10, title="Tablet", price=45.38
    )

    update_payload = {
        "title": "",  # Invalid: empty title
        "description": "Updated Description",
        "price": -50.0,  # Invalid: negative price
    }

    response = client.put(f"/products/{created.id}", json=update_payload)

    assert response.status_code == 400
    assert response.headers["content-type"] == "application/problem+json"

    _assert_problem_response(
        response, expected_title="Bad Request", expected_status=400
    )


def test_update_existing_product_with_missing_fields_response(
    client: TestClient,
) -> None:
    """Validate that updating an existing product with missing required fields returns 400 with the expected schema."""
    created: Product = _create_and_assert_product(
        client, seller_id=11, title="Smartphone", price=299.99
    )

    update_payload = {
        "description": "Updated Description",
        # Missing title and price
    }

    response = client.put(f"/products/{created.id}", json=update_payload)

    assert response.status_code == 400
    assert response.headers["content-type"] == "application/problem+json"

    _assert_problem_response(
        response, expected_title="Bad Request", expected_status=400
    )


def test_update_existing_product_returns_updated_fields(client: TestClient) -> None:
    """Test that product update returns the updated fields."""
    created = _create_and_assert_product(
        client, seller_id=5, title="Laptop", price=1200.0
    )

    update_payload = {
        "title": "Laptop Pro",
        "description": "Updated description",
        "price": 1400.456,
    }

    response = client.put(f"/products/{created.id}", json=update_payload)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    body: ProductResponse = ProductResponse.model_validate(
        response.json(), extra="forbid"
    )
    updated: Product = Product.model_validate(body.data, extra="forbid")

    assert updated.id == created.id
    assert updated.sellerId == created.sellerId
    assert updated.title == update_payload["title"]
    assert updated.description == update_payload["description"]
    assert updated.price == round_to_two_decimals_half_up(update_payload["price"])


def test_update_existing_product_persists_changes(client: TestClient) -> None:
    """Validate that updates to a product are persisted and reflected in subsequent retrievals."""
    created = _create_and_assert_product(
        client, seller_id=6, title="Camera", price=549.99
    )

    update_payload = {
        "title": "Camera X",
        "description": "Updated description for Camera X",
        "price": 599.99,
    }

    update_response = client.put(f"/products/{created.id}", json=update_payload)
    assert update_response.status_code == 200

    body: ProductResponse = ProductResponse.model_validate(
        update_response.json(), extra="forbid"
    )
    updated: Product = Product.model_validate(body.data, extra="forbid")

    get_response = client.get(f"/products/{created.id}")
    assert get_response.status_code == 200

    body: ProductResponse = ProductResponse.model_validate(
        get_response.json(), extra="forbid"
    )
    retrieved: Product = Product.model_validate(body.data, extra="forbid")

    assert updated == retrieved
    assert retrieved.id == created.id
    assert retrieved.sellerId == created.sellerId
    assert retrieved.title == update_payload["title"]
    assert retrieved.description == update_payload["description"]
    assert retrieved.price == round_to_two_decimals_half_up(update_payload["price"])


# DELETE /products/{id}
def test_delete_nonexistent_product_response(client: TestClient) -> None:
    """Check that deleting a non-existent product returns 404 with the expected schema."""
    response = client.delete("/products/78")

    _assert_problem_response(
        response, expected_title="Product not found", expected_status=404
    )


def test_delete_existing_product_response(client: TestClient) -> None:
    """Confirm that deleting a product returns 204 and removes it from listing."""
    created = _create_and_assert_product(
        client, seller_id=7, title="Printer", price=199.99
    )

    delete_response = client.delete(f"/products/{created.id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/products/{created.id}")
    _assert_problem_response(
        get_response, expected_title="Product not found", expected_status=404
    )
