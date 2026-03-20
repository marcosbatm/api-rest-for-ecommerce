from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.config import Config
from src.repository.orm import (
    Base,
    CartItemORM,
    CartORM,
    ProductORM,
    set_cart_timestamps,
    set_product_timestamps,
    utcnow,
)
from src.repository.repository import Repository
from src.models.cart import Cart, CartItem
from src.models.product import CreateProductRequest, Product, UpdateProductRequest


class RepositoryDatabase(Repository):
    def __init__(self, config: Config):
        self.config = config
        self.engine = create_engine(
            f"postgresql://{config.database_user}:{config.database_password}"
            f"@{config.database_host}:{config.database_port}/{config.database_name}",
            echo=False,
            pool_pre_ping=True,
        )

        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

        # Crear tablas si no existen
        Base.metadata.create_all(self.engine)

    def _get_session(self) -> Session:
        return self.SessionLocal()

    @staticmethod
    def _to_product(product: ProductORM) -> Product:
        return Product(
            id=product.id,
            sellerId=product.seller_id,
            title=product.title,
            description=product.description,
            price=product.price,
            createdAt=product.created_at,
            updatedAt=product.updated_at,
        )

    @staticmethod
    def _to_cart_item(item: CartItemORM) -> CartItem:
        return CartItem(
            id=item.id,
            productId=item.product_id,
            title=item.title,
            unitPrice=item.unit_price,
            addedAt=item.added_at,
        )

    def _to_cart(self, cart: CartORM) -> Cart:
        items = {item.id: self._to_cart_item(item) for item in cart.items}
        return Cart(userId=cart.user_id, items=items, totalPrice=cart.total_price)

    def _get_cart_or_create_orm(self, session: Session, userId: int) -> CartORM:
        cart = session.query(CartORM).filter(CartORM.user_id == userId).first()
        if cart is None:
            cart = CartORM(user_id=userId, total_price=0.0)
            set_cart_timestamps(cart)
            session.add(cart)
            session.commit()
            session.refresh(cart)
        return cart

    def add_product(self, productRequest: CreateProductRequest) -> Product:
        session = self._get_session()
        try:
            product = ProductORM(
                seller_id=productRequest.sellerId,
                title=productRequest.title,
                description=productRequest.description,
                price=productRequest.price,
            )
            set_product_timestamps(product)
            session.add(product)
            session.commit()
            session.refresh(product)
            return self._to_product(product)
        finally:
            session.close()

    def get_product_snapshot_or_fail(self, id: int) -> Product:
        session = self._get_session()
        try:
            product = session.get(ProductORM, id)
            if product is None:
                raise KeyError(f"Product with id {id} not found")
            return self._to_product(product)
        finally:
            session.close()

    def snapshot_all_products(self) -> list[Product]:
        session = self._get_session()
        try:
            products = session.query(ProductORM).order_by(ProductORM.id.asc()).all()
            return [self._to_product(product) for product in products]
        finally:
            session.close()

    def update_product(
        self, id: int, productRequest: UpdateProductRequest
    ) -> Product | None:
        session = self._get_session()
        try:
            product = session.get(ProductORM, id)
            if not product:
                return None

            product.title = productRequest.title
            product.description = productRequest.description
            product.price = productRequest.price
            product.updated_at = datetime.now(UTC)

            session.commit()
            session.refresh(product)
            return self._to_product(product)
        finally:
            session.close()

    def delete_product(self, id: int) -> bool:
        session = self._get_session()
        try:
            product = session.get(ProductORM, id)
            if not product:
                return False

            session.delete(product)
            session.commit()
            return True
        finally:
            session.close()

    # CART METHODS
    def _get_cart_or_create(self, userId: int) -> Cart:
        session = self._get_session()
        try:
            cart = self._get_cart_or_create_orm(session, userId)
            session.refresh(cart)
            return self._to_cart(cart)
        finally:
            session.close()

    def get_cart_snapshot(self, userId: int) -> Cart:
        return self._get_cart_or_create(userId)

    def clear_cart(self, userId: int) -> None:
        session = self._get_session()
        try:
            cart = self._get_cart_or_create_orm(session, userId)
            cart.items.clear()
            cart.total_price = 0.0
            cart.updated_at = utcnow()
            session.commit()
        finally:
            session.close()

    def add_snapshot_to_cart(self, userId: int, product_snapshot: Product) -> CartItem:
        session = self._get_session()
        try:
            cart = self._get_cart_or_create_orm(session, userId)
            new_item = CartItemORM(
                cart_id=cart.id,
                product_id=product_snapshot.id,
                title=product_snapshot.title,
                unit_price=product_snapshot.price,
                added_at=utcnow(),
            )
            session.add(new_item)
            cart.total_price += new_item.unit_price
            cart.updated_at = utcnow()
            session.commit()
            session.refresh(new_item)
            return self._to_cart_item(new_item)
        finally:
            session.close()

    def remove_item_from_cart_or_fail(self, userId: int, cartItemId: int) -> None:
        session = self._get_session()
        try:
            cart = self._get_cart_or_create_orm(session, userId)
            item = (
                session.query(CartItemORM)
                .filter(CartItemORM.cart_id == cart.id, CartItemORM.id == cartItemId)
                .first()
            )
            if item is None:
                raise KeyError(f"Cart item with id {cartItemId} not found")

            cart.total_price = max(0.0, cart.total_price - item.unit_price)
            cart.updated_at = utcnow()
            session.delete(item)
            session.commit()
        finally:
            session.close()
