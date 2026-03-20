from src.repository.repository import Repository
from src.models.product import CreateProductRequest, Product, UpdateProductRequest
from src.models.cart import Cart, CartItem


class EcommerceBackend:
    def __init__(self, repository: Repository):
        self.repository: Repository = repository

    def create_product(self, productRequest: CreateProductRequest) -> Product | None:
        # Logica de negocio: round price to 2 decimal places
        productRequest.price = round(productRequest.price, 2)
        return self.repository.add_product(productRequest)

    def read_products(self) -> dict:
        data = self.repository.snapshot_all_products()
        # Logica de negocio: ordenar productos por id ascendente
        data.sort(key=lambda p: p.id)
        return {"data": data}

    def read_product_or_fail(self, id: int) -> Product | None:
        return self.repository.get_product_snapshot_or_fail(id)

    def update_product(
        self, id: int, productRequest: UpdateProductRequest
    ) -> Product | None:
        # Logica de negocio: round price to 2 decimal places
        productRequest.price = round(productRequest.price, 2)
        return self.repository.update_product(id, productRequest)

    def delete_product(self, id: int) -> bool:
        return self.repository.delete_product(id)

    # CART METHODS:

    def read_cart(self, userId: int) -> Cart:
        return self.repository.get_cart_snapshot(userId)

    def clear_cart(self, userId: int) -> None:
        self.repository.clear_cart(userId)

    def add_item_to_cart_or_fail(self, userId: int, productId: int) -> CartItem:
        product_snapshot = self.repository.get_product_snapshot_or_fail(productId)
        return self.repository.add_snapshot_to_cart(userId, product_snapshot)

    def remove_item_from_cart_or_fail(self, userId: int, cartItemId: int) -> None:
        self.repository.remove_item_from_cart_or_fail(userId, cartItemId)
