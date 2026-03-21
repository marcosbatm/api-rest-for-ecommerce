import logging

from src.repository.repository import Repository
from src.models.product import CreateProductRequest, Product, UpdateProductRequest
from src.models.cart import Cart, CartItem


logger = logging.getLogger(__name__)


class EcommerceBackend:
    def __init__(self, repository: Repository):
        self.repository: Repository = repository
        logger.info(
            "EcommerceBackend initialized with repository=%s", type(repository).__name__
        )

    def create_product(self, productRequest: CreateProductRequest) -> Product | None:
        logger.debug("Creating product sellerId=%s", productRequest.sellerId)
        # Logica de negocio: round price to 2 decimal places
        productRequest.price = round(productRequest.price, 2)
        product = self.repository.add_product(productRequest)
        logger.info("Product created id=%s", product.id)
        return product

    def read_products(self) -> dict:
        logger.debug("Reading all products")
        data = self.repository.snapshot_all_products()
        # Logica de negocio: ordenar productos por id ascendente
        data.sort(key=lambda p: p.id)
        logger.debug("Read %s products", len(data))
        return {"data": data}

    def read_product_or_fail(self, id: int) -> Product:
        logger.debug("Reading product id=%s", id)
        return self.repository.get_product_snapshot_or_fail(id)

    def update_product(
        self, id: int, productRequest: UpdateProductRequest
    ) -> Product | None:
        logger.debug("Updating product id=%s", id)
        # Logica de negocio: round price to 2 decimal places
        productRequest.price = round(productRequest.price, 2)
        product = self.repository.update_product(id, productRequest)
        if product is None:
            logger.warning("Product not found for update id=%s", id)
        else:
            logger.info("Product updated id=%s", id)
        return product

    def delete_product(self, id: int) -> bool:
        logger.debug("Deleting product id=%s", id)
        deleted = self.repository.delete_product(id)
        if deleted:
            logger.info("Product deleted id=%s", id)
        else:
            logger.warning("Product not found for delete id=%s", id)
        return deleted

    # CART METHODS:

    def read_cart(self, userId: int) -> Cart:
        logger.debug("Reading cart userId=%s", userId)
        return self.repository.get_cart_snapshot(userId)

    def clear_cart(self, userId: int) -> None:
        logger.debug("Clearing cart userId=%s", userId)
        self.repository.clear_cart(userId)

    def add_item_to_cart_or_fail(self, userId: int, productId: int) -> CartItem:
        logger.debug("Adding item to cart userId=%s productId=%s", userId, productId)
        if userId <= 0 or productId <= 0:
            logger.warning(
                "Invalid cart item input userId=%s productId=%s",
                userId,
                productId,
            )
            raise ValueError("userId and productId must be positive integers")
        product_snapshot = self.repository.get_product_snapshot_or_fail(productId)
        cart_item = self.repository.add_snapshot_to_cart(userId, product_snapshot)
        logger.info(
            "Cart item added userId=%s cartItemId=%s productId=%s",
            userId,
            cart_item.id,
            productId,
        )
        return cart_item

    def remove_item_from_cart_or_fail(self, userId: int, cartItemId: int) -> None:
        logger.debug("Removing cart item userId=%s cartItemId=%s", userId, cartItemId)
        self.repository.remove_item_from_cart_or_fail(userId, cartItemId)
        logger.info("Cart item removed userId=%s cartItemId=%s", userId, cartItemId)
