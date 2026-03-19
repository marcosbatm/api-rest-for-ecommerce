from src.database.database import Repository
from src.models.product import CreateProductRequest, Product, UpdateProductRequest
from src.models.cart import Cart, CartItem


class EcommerceBackend:
    def __init__(self, database: Repository):
        self.database: Repository = database

    def create_product(self, productRequest: CreateProductRequest) -> Product | None:
        # Logica de negocio: round price to 2 decimal places
        productRequest.price = round(productRequest.price, 2)
        return self.database.add_product(productRequest)

    def read_products(self) -> dict:
        data = self.database.snapshot_all_products()
        # Logica de negocio: ordenar productos por id ascendente
        data.sort(key=lambda p: p.id)
        return {"data": data}

    def read_product(self, id: int) -> Product | None:
        return self.database.get_product_snapshot_or_fail(id)

    def update_product(
        self, id: int, productRequest: UpdateProductRequest
    ) -> Product | None:
        # Logica de negocio: round price to 2 decimal places
        productRequest.price = round(productRequest.price, 2)
        return self.database.update_product(id, productRequest)

    def delete_product(self, id: int) -> bool:
        return self.database.delete_product(id)

    # CART METHODS:

    def read_cart(self, userId: int) -> Cart:
        return self.database.get_cart_snapshot(userId)

    def clear_cart(self, userId: int) -> None:
        self.database.clear_cart(userId)

    def add_item_to_cart_or_fail(self, userId: int, productId: int) -> CartItem:
        product_snapshot = self.database.get_product_snapshot_or_fail(productId)
        return self.database.add_snapshot_to_cart(userId, product_snapshot)
