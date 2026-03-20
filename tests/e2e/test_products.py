import pytest
from fastapi.testclient import TestClient


def _create_product(
    client: TestClient, *, seller_id: int, title: str, price: float
) -> dict:
    """Create a product through the API and return the created resource payload."""
    payload = {
        "sellerId": seller_id,
        "title": title,
        "description": f"Description for {title}",
        "price": price,
    }
    response = client.post("/products", json=payload)
    assert response.status_code == 201
    return response.json()["data"]


# POST /products
def test_create_product_returns_201(client: TestClient) -> None:
    """Validate that creating a product returns 201 and persists expected data."""
    payload = {
        "sellerId": 101,
        "title": "Keyboard",
        "description": "Mechanical keyboard",
        "price": 149.995,
    }

    response = client.post("/products", json=payload)

    assert response.status_code == 201
    body = response.json()["data"]
    assert isinstance(body["id"], int)
    assert body["sellerId"] == payload["sellerId"]
    assert body["title"] == payload["title"]
    assert body["description"] == payload["description"]
    assert body["price"] == pytest.approx(150.0)


def test_create_product_with_negative_seller_id_returns_400(client: TestClient) -> None:
    """Validate that creating a product with a negative sellerId returns 400 with the expected error."""
    payload = {
        "sellerId": -1,
        "title": "Invalid Product",
        "description": "Product with negative seller",
        "price": 50.0,
    }

    response = client.post("/products", json=payload)

    assert response.status_code == 400
    assert response.headers["content-type"] == "application/problem+json"
    body = response.json()
    assert body["title"] == "Bad Request"
    assert body["status"] == 400
    assert "detail" in body
    assert "instance" in body


# GET /products
def test_get_products_returns_all_ordered_by_id(client: TestClient) -> None:
    """Verify that listing returns all products sorted by ascending id."""
    first = _create_product(client, seller_id=1, title="Mouse", price=10.0)
    second = _create_product(client, seller_id=2, title="Keyboard", price=149.99)
    third = _create_product(client, seller_id=3, title="Speaker", price=89.99)

    response = client.get("/products")

    assert response.status_code == 200
    products = response.json()["data"]
    assert [product["id"] for product in products] == [
        first["id"],
        second["id"],
        third["id"],
    ]


# GET /products/{id}
def test_get_product_by_id_returns_200(client: TestClient) -> None:
    """Check that an existing product can be retrieved by id with status 200."""
    created = _create_product(client, seller_id=9, title="Headset", price=79.99)

    response = client.get(f"/products/{created['id']}")

    assert response.status_code == 200
    product = response.json()["data"]
    assert product["id"] == created["id"]
    assert product["title"] == "Headset"


def test_get_nonexistent_product_returns_404(client: TestClient) -> None:
    """Check that fetching a non-existent product returns 404 with the expected schema."""
    response = client.get("/products/999999")

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    body = response.json()
    assert body["title"] == "Product not found"
    assert body["status"] == 404
    assert "detail" in body
    assert "999999" in body["detail"]
    assert body["instance"] == "/products/999999"


# PUT /products/{id}
def test_update_product_returns_updated_fields(client: TestClient) -> None:
    """Ensure that product update persists the new fields."""
    created = _create_product(client, seller_id=5, title="Laptop", price=1200.0)

    update_payload = {
        "title": "Laptop Pro",
        "description": "Updated description",
        "price": 1400.456,
    }

    response = client.put(f"/products/{created['id']}", json=update_payload)

    assert response.status_code == 200
    updated = response.json()["data"]
    assert updated["id"] == created["id"]
    assert updated["sellerId"] == created["sellerId"]
    assert updated["title"] == "Laptop Pro"
    assert updated["description"] == "Updated description"
    assert updated["price"] == pytest.approx(1400.46)


def test_update_nonexistent_product_returns_404(client: TestClient) -> None:
    """Validate that updating a non-existent product returns 404 with the expected schema."""
    update_payload = {
        "title": "Updated Title",
        "description": "Updated Description",
        "price": 100.0,
    }

    response = client.put("/products/999999", json=update_payload)

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    body = response.json()
    assert body["title"] == "Product not found"
    assert body["status"] == 404
    assert "detail" in body
    assert "999999" in body["detail"]
    assert body["instance"] == "/products/999999"


# DELETE /products/{id}
def test_delete_product_returns_204(client: TestClient) -> None:
    """Confirm that deleting a product returns 204 and removes it from listing."""
    created = _create_product(client, seller_id=8, title="Webcam", price=49.99)

    delete_response = client.delete(f"/products/{created['id']}")

    assert delete_response.status_code == 204

    list_response = client.get("/products")
    assert list_response.status_code == 200
    assert list_response.json()["data"] == []


def test_delete_nonexistent_product_returns_404(client: TestClient) -> None:
    """Check that deleting a non-existent product returns 404 with the expected schema."""
    response = client.delete("/products/999999")

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    body = response.json()
    assert body["title"] == "Product not found"
    assert body["status"] == 404
    assert "detail" in body
    assert "999999" in body["detail"]
    assert body["instance"] == "/products/999999"
