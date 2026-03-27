import logging
import time

from src.repository.repository import Repository
from src.models.cart import Cart, CartItem
from src.models.product import CreateProductRequest, Product, UpdateProductRequest


logger = logging.getLogger(__name__)


class RepositoryMemory(Repository):
    """
    Capa Repository: Encapsula la conexión a la base de datos.
    Utiliza config para configurar la conexión.
    Si no recibe config, asume una base de datos en memoria (dict).
    """

    def __init__(self):
        self.productDatabase: dict[int, Product] = {}
        self.last_product_id = 0

        self.cartDatabase: dict[int, Cart] = {}
        self.last_cart_id = 0

        self.cartItemDatabase: dict[int, CartItem] = {}
        self.last_item_id = 0
        logger.info("Initialized in-memory repository")

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
        logger.debug("In-memory product created id=%s", product.id)
        return product

    def get_product_snapshot_or_fail(self, id: int) -> Product:
        product = self.productDatabase.get(id)
        if not product:
            logger.warning("In-memory product not found id=%s", id)
            raise KeyError(f"Product with id {id} not found")
        return product.model_copy(deep=True)

    def snapshot_all_products(self) -> list[Product]:
        logger.debug(
            "In-memory snapshot all products count=%s", len(self.productDatabase)
        )
        return [p.model_copy(deep=True) for p in self.productDatabase.values()]

    def update_product(
        self, id: int, productRequest: UpdateProductRequest
    ) -> Product | None:
        existing_product = self.productDatabase.get(id)
        if not existing_product:
            logger.warning("In-memory product not found for update id=%s", id)
            return None
        updated_product = Product(
            id=id,
            sellerId=existing_product.sellerId,
            title=productRequest.title,
            description=productRequest.description,
            price=productRequest.price,
            createdAt=existing_product.createdAt,
            updatedAt=time.time(),
        )
        self.productDatabase[id] = updated_product
        logger.debug("In-memory product updated id=%s", id)
        return updated_product

    def delete_product(self, id: int) -> bool:
        existing_product = self.productDatabase.get(id)
        if not existing_product:
            logger.warning("In-memory product not found for delete id=%s", id)
            return False
        del self.productDatabase[id]
        logger.debug("In-memory product deleted id=%s", id)
        return True

    # CART METHODS:
    def _get_cart_or_create(self, userId: int) -> Cart:
        cart = self.cartDatabase.get(userId)
        if not cart:
            cart = Cart(userId=userId, items=[], totalPrice=0.0)
            self.cartDatabase[userId] = cart
            logger.debug("In-memory cart created userId=%s", userId)
        return cart

    def get_cart_snapshot(self, userId: int) -> Cart:
        cart = self._get_cart_or_create(userId)
        return cart.model_copy(deep=True)

    def clear_cart(self, userId: int) -> None:
        self.cartDatabase[userId] = Cart(userId=userId, items=[], totalPrice=0.0)
        logger.debug("In-memory cart cleared userId=%s", userId)
        return

    def add_snapshot_to_cart(self, userId: int, product_snapshot: Product) -> CartItem:
        cart = self.cartDatabase.get(userId)
        if not cart:
            cart = Cart(userId=userId, items={}, totalPrice=0.0)

        new_item = CartItem(
            id=self.last_item_id + 1,
            productId=product_snapshot.id,
            title=product_snapshot.title,
            unitPrice=product_snapshot.price,
            addedAt=time.time(),
        )

        cart.items[new_item.id] = new_item
        cart.totalPrice += new_item.unitPrice
        self.cartDatabase[userId] = cart
        self.last_item_id += 1
        logger.debug(
            "In-memory cart item created userId=%s cartItemId=%s productId=%s",
            userId,
            new_item.id,
            product_snapshot.id,
        )
        return new_item

    def remove_item_from_cart_or_fail(self, userId: int, cartItemId: int) -> None:
        cart = self._get_cart_or_create(userId)
        removed_item = cart.items.pop(cartItemId)  # Si falla lanza KeyError
        cart.totalPrice -= removed_item.unitPrice
        logger.debug(
            "In-memory cart item removed userId=%s cartItemId=%s", userId, cartItemId
        )

    def remove_cart_items_by_product_id(self, productId: int) -> None:
        for cart in self.cartDatabase.values():
            items_to_remove = [
                item_id
                for item_id, item in cart.items.items()
                if item.productId == productId
            ]
            for item_id in items_to_remove:
                removed_item = cart.items.pop(item_id)
                cart.totalPrice -= removed_item.unitPrice
                logger.debug(
                    "In-memory cart item removed due to product delete userId=%s cartItemId=%s productId=%s",
                    cart.userId,
                    item_id,
                    productId,
                )
