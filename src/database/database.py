import time
from src.models.product import CreateProductRequest, Product


class Repository:
    def __init__(self, config):
        self.config = config
        self.productDatabase: dict[int, Product] = {}
        self.last_product_id = 0

    def add_product(self, productRequest: CreateProductRequest) -> Product:
        now = time.time()
        product = Product(
            id=self.last_product_id + 1,
            sellerId=productRequest.sellerId,
            title=productRequest.title,
            description=productRequest.description,
            price=productRequest.price,
            createdAt=now,
            updatedAt=now,
        )
        self.productDatabase[product.id] = product
        self.last_product_id += 1
        return product

    def get_product(self, id: int) -> Product | None:
        return self.productDatabase.get(id)

    def get_all_products(self) -> list[Product]:
        return list(self.productDatabase.values())
