import pytest
from datetime import datetime

from src.repository.repositoryMemory import RepositoryMemory
from src.models.product import CreateProductRequest, Product


def test_memory_repository_starts_empty():
    repo = RepositoryMemory()
    products = repo.snapshot_all_products()
    assert isinstance(products, list)
    assert products == []


def test_repository_add_product_success():
    repo = RepositoryMemory()
    product_request = CreateProductRequest(
        sellerId=1,
        title="Test Product",
        description="A product for testing",
        price=9.99,
    )
    product: Product = repo.add_product(product_request)
    # TODO: separar en varios tests unitarios.
    assert product.id is not None and product.id >= 0 and isinstance(product.id, int)
    assert product.sellerId == product_request.sellerId
    assert product.title == product_request.title
    assert product.description == product_request.description
    assert product.price == product_request.price
    assert product.createdAt is not None and isinstance(product.createdAt, datetime)
    assert product.updatedAt is not None and isinstance(product.updatedAt, datetime)
    assert product.createdAt == product.updatedAt


def test_repository_get_product_success():
    repo = RepositoryMemory()
    product_request = CreateProductRequest(
        sellerId=1,
        title="Test Product",
        description="A product for testing",
        price=9.99,
    )
    added_product: Product = repo.add_product(product_request)
    retrieved_product: Product = repo.get_product_snapshot_or_fail(added_product.id)
    assert retrieved_product is not None
    assert retrieved_product == added_product


def test_repository_get_invalid_product():
    repo = RepositoryMemory()
    # This should fail, assert it raises exception using pytest:
    with pytest.raises(KeyError):
        repo.get_product_snapshot_or_fail(1)


def test_repository_get_all_products_success():
    repo = RepositoryMemory()
    product_requests = [
        CreateProductRequest(
            sellerId=1,
            title="Test Product",
            description="A product for testing",
            price=9.99,
        ),
        CreateProductRequest(
            sellerId=2,
            title="Another Product",
            description="Another product for testing",
            price=19.99,
        ),
    ]
    products: list[Product] = []
    for req in product_requests:
        products.append(repo.add_product(req))

    retrieved_products = repo.snapshot_all_products()
    assert len(retrieved_products) == len(product_requests)
    for prod in products:
        assert any(rp == prod for rp in retrieved_products)


# def test_repository_persists_data():
#     pass
