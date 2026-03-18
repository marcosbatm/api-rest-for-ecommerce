from src.database.database import Repository


def test_repository_starts_empty():
    repo = Repository(config=None)
    products = repo.get_all_products()
    assert isinstance(products, list)
    assert products == []
