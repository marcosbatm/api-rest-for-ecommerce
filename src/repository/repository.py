from abc import ABC, abstractmethod

from src.models.cart import Cart, CartItem
from src.models.product import CreateProductRequest, Product, UpdateProductRequest


class Repository(ABC):
    """
    Contrato base para repositorios de datos.
    Las clases concretas que hereden de esta clase deben implementar
    el manejo de persistencia según corresponda (memoria, SQL, etc.).
    """

    @abstractmethod
    def add_product(self, productRequest: CreateProductRequest) -> Product:
        pass

    @abstractmethod
    def get_product_snapshot_or_fail(self, id: int) -> Product:
        pass

    @abstractmethod
    def snapshot_all_products(self) -> list[Product]:
        pass

    @abstractmethod
    def update_product(
        self, id: int, productRequest: UpdateProductRequest
    ) -> Product | None:
        pass

    @abstractmethod
    def delete_product(self, id: int) -> bool:
        pass

    @abstractmethod
    def _get_cart_or_create(self, userId: int) -> Cart:
        """Versión abstracta del helper interno de carrito."""
        pass

    @abstractmethod
    def get_cart_snapshot(self, userId: int) -> Cart:
        pass

    @abstractmethod
    def clear_cart(self, userId: int) -> None:
        pass

    @abstractmethod
    def add_snapshot_to_cart(self, userId: int, product_snapshot: Product) -> CartItem:
        pass

    @abstractmethod
    def remove_item_from_cart_or_fail(self, userId: int, cartItemId: int) -> None:
        pass

    @abstractmethod
    def remove_cart_items_by_product_id(self, productId: int) -> None:
        """Elimina de todos los carritos los items relacionados al productId dado. Usado para mantener consistencia al eliminar un producto."""
        pass
