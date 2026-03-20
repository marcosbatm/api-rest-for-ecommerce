import time

from src.repository.repository import Repository
from src.models.cart import Cart, CartItem
from src.models.product import CreateProductRequest, Product, UpdateProductRequest


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

    def get_product_snapshot_or_fail(self, id: int) -> Product:
        product = self.productDatabase.get(id)
        if not product:
            raise KeyError(f"Product with id {id} not found")
        return product.model_copy(deep=True)

    def snapshot_all_products(self) -> list[Product]:
        return [p.model_copy(deep=True) for p in self.productDatabase.values()]

    def update_product(
        self, id: int, productRequest: UpdateProductRequest
    ) -> Product | None:
        existing_product = self.productDatabase.get(id)
        if not existing_product:
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
        return updated_product

    def delete_product(self, id: int) -> bool:
        existing_product = self.productDatabase.get(id)
        if not existing_product:
            return False
        del self.productDatabase[id]
        return True

    # CART METHODS:
    def _get_cart_or_create(self, userId: int) -> Cart:
        cart = self.cartDatabase.get(userId)
        if not cart:
            cart = Cart(userId=userId, items=[], totalPrice=0.0)
            self.cartDatabase[userId] = cart
        return cart

    def get_cart_snapshot(self, userId: int) -> Cart:
        cart = self._get_cart_or_create(userId)
        return cart.model_copy(deep=True)

    def clear_cart(self, userId: int) -> None:
        self.cartDatabase[userId] = Cart(userId=userId, items=[], totalPrice=0.0)
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
        return new_item

    def remove_item_from_cart_or_fail(self, userId: int, cartItemId: int) -> None:
        cart = self._get_cart_or_create(userId)
        removed_item = cart.items.pop(cartItemId)  # Si falla lanza KeyError
        cart.totalPrice -= removed_item.unitPrice
