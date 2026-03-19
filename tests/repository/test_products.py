from src.database.database import Repository
from src.models.product import CreateProductRequest, Product


def test_memory_repository_starts_empty():
    repo = Repository(config=None)
    products = repo.get_all_products()
    assert isinstance(products, list)
    assert products == []


def test_repository_add_product_success():
    repo = Repository(config=None)
    product_request = CreateProductRequest(
        sellerId=1,
        title="Test Product",
        description="A product for testing",
        price=9.99,
    )
    product: Product = repo.add_product(product_request)
    assert product.id == 1
    assert product.sellerId == 1
    assert product.title == "Test Product"
    assert product.description == "A product for testing"
    assert product.price == 9.99


def test_repository_get_product_success():
    repo = Repository(config=None)
    product_request = CreateProductRequest(
        sellerId=1,
        title="Test Product",
        description="A product for testing",
        price=9.99,
    )
    added_product: Product = repo.add_product(product_request)
    retrieved_product: Product = repo.get_product(added_product.id)
    assert retrieved_product is not None
    assert retrieved_product.id == added_product.id
    assert retrieved_product.sellerId == added_product.sellerId
    assert retrieved_product.title == added_product.title
    assert retrieved_product.description == added_product.description
    assert retrieved_product.price == added_product.price


def test_repository_get_all_products_success():
    repo = Repository(config=None)
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

    retrieved_products = repo.get_all_products()
    assert len(retrieved_products) == len(product_requests)
    for prod in products:
        assert any(rp == prod for rp in retrieved_products)
