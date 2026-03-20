from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ProductORM(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(2000), nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)


class CartORM(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    total_price = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    items = relationship(
        "CartItemORM",
        back_populates="cart",
        cascade="all, delete-orphan",
        order_by="CartItemORM.id",
    )


class CartItemORM(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    unit_price = Column(Float, nullable=False)
    added_at = Column(DateTime(timezone=True), nullable=False)

    cart = relationship("CartORM", back_populates="items")


def utcnow() -> datetime:
    return datetime.now(UTC)


def set_product_timestamps(product: ProductORM) -> ProductORM:
    now = datetime.now(UTC)
    product.created_at = now
    product.updated_at = now
    return product


def set_cart_timestamps(cart: CartORM) -> CartORM:
    now = datetime.now(UTC)
    cart.created_at = now
    cart.updated_at = now
    return cart
