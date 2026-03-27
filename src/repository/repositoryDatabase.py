import logging

from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.config_app import Config
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


logger = logging.getLogger(__name__)


class RepositoryDatabase(Repository):
    def __init__(self, config: Config):
        self.config = config
        logger.info(
            "Initializing database repository host=%s port=%s db=%s",
            config.database_host,
            config.database_port,
            config.database_name,
        )
        self.engine = create_engine(
            f"postgresql://{config.database_user}:{config.database_password}"
            f"@{config.database_host}:{config.database_port}/{config.database_name}",
            echo=False,
            pool_pre_ping=True,
        )

        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

        # Crear tablas si no existen
        Base.metadata.create_all(self.engine)
        logger.info("Database tables ensured")

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
        items = [self._to_cart_item(item) for item in cart.items]
        items.sort(key=lambda x: (-x.addedAt.timestamp(), -x.id))
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
            logger.debug("DB product created id=%s", product.id)
            return self._to_product(product)
        finally:
            session.close()

    def get_product_snapshot_or_fail(self, id: int) -> Product:
        session = self._get_session()
        try:
            product = session.get(ProductORM, id)
            if product is None:
                logger.warning("DB product not found id=%s", id)
                raise KeyError(f"Product with id {id} not found")
            return self._to_product(product)
        finally:
            session.close()

    def snapshot_all_products(self) -> list[Product]:
        session = self._get_session()
        try:
            products = session.query(ProductORM).order_by(ProductORM.id.asc()).all()
            logger.debug("DB snapshot all products count=%s", len(products))
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
                logger.warning("DB product not found for update id=%s", id)
                return None

            product.title = productRequest.title
            product.description = productRequest.description
            product.price = productRequest.price
            product.updated_at = datetime.now(UTC)

            session.commit()
            session.refresh(product)
            logger.debug("DB product updated id=%s", id)
            return self._to_product(product)
        finally:
            session.close()

    def delete_product(self, id: int) -> bool:
        session = self._get_session()
        try:
            product = session.get(ProductORM, id)
            if not product:
                logger.warning("DB product not found for delete id=%s", id)
                return False

            session.delete(product)
            session.commit()
            logger.debug("DB product deleted id=%s", id)
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
            logger.debug("DB cart cleared userId=%s", userId)
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
            logger.debug(
                "DB cart item created userId=%s cartItemId=%s productId=%s",
                userId,
                new_item.id,
                product_snapshot.id,
            )
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
                logger.warning(
                    "DB cart item not found userId=%s cartItemId=%s", userId, cartItemId
                )
                raise KeyError(f"Cart item with id {cartItemId} not found")

            cart.total_price = max(0.0, cart.total_price - item.unit_price)
            cart.updated_at = utcnow()
            session.delete(item)
            session.commit()
            logger.debug(
                "DB cart item removed userId=%s cartItemId=%s", userId, cartItemId
            )
        finally:
            session.close()

    def remove_cart_items_by_product_id(self, productId):
        session = self._get_session()
        try:
            items_to_remove = (
                session.query(CartItemORM)
                .filter(CartItemORM.product_id == productId)
                .all()
            )
            for item in items_to_remove:
                cart = session.query(CartORM).filter(CartORM.id == item.cart_id).first()
                if cart:
                    cart.total_price = max(0.0, cart.total_price - item.unit_price)
                    cart.updated_at = utcnow()
                session.delete(item)
            session.commit()
            logger.debug(
                "DB cart items removed by productId=%s count=%s",
                productId,
                len(items_to_remove),
            )
        finally:
            session.close()
