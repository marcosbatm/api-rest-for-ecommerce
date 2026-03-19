from src.database.database import Repository
from src.models.product import CreateProductRequest, Product


class EcommerceBackend:
    def __init__(self, database: Repository):
        self.database = database

    def create_product(self, productRequest: CreateProductRequest) -> Product | None:
        # Logica de negocio: round price to 2 decimal places
        productRequest.price = round(productRequest.price, 2)
        return self.database.add_product(productRequest)

    def read_products(self) -> dict:
        return {"data": self.database.get_all_products()}

    def read_product(self, id: int) -> dict:
        product = self.database.get_product(id)
        if not product:
            return {"error": "Product not found"}
        return {"data": product}
