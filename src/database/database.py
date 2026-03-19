import time
from src.models.cart import Cart
from src.models.product import CreateProductRequest, Product, UpdateProductRequest


class Repository:
    """
    Capa Repository: Encapsula la conexión a la base de datos.
    Utiliza config para configurar la conexión.
    Si no recibe config, asume una base de datos en memoria (dict).
    """

    def __init__(self, config: dict | None):
        if config is None:
            self.config = config
            self.productDatabase: dict[int, Product] = {}
            self.last_product_id = 0
        else:
            # Aquí podríamos implementar la lógica para conectar a una base de datos real
            raise NotImplementedError("Database connection not implemented yet")

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

    def get_cart(self, userId: int) -> Cart:
        # TODO: Implementar lógica real de carrito, con persistencia y manejo de items.
        return Cart(userId=userId, items=[], totalPrice=0.0)
