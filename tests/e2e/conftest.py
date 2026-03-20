import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from src.repository.orm import Base


TABLES_TO_TRUNCATE = ("cart_items", "carts", "products")


def _build_test_database_url() -> str:
    """Build the PostgreSQL connection URL for the test database."""
    host = os.getenv("TEST_DATABASE_HOST", "localhost")
    port = os.getenv("TEST_DATABASE_PORT", "5433")
    name = os.getenv("TEST_DATABASE_NAME", "test_db")
    user = os.getenv("TEST_DATABASE_USER", "test_user")
    password = os.getenv("TEST_DATABASE_PASSWORD", "test_password")
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


@pytest.fixture(scope="session", autouse=True)
def configure_testing_environment() -> None:
    """Map TEST_DATABASE_* vars into DATABASE_* so Config uses the test DB."""
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["MOCK_DB"] = "false"
    os.environ["DATABASE_HOST"] = os.getenv("TEST_DATABASE_HOST", "localhost")
    os.environ["DATABASE_PORT"] = os.getenv("TEST_DATABASE_PORT", "5433")
    os.environ["DATABASE_NAME"] = os.getenv("TEST_DATABASE_NAME", "test_db")
    os.environ["DATABASE_USER"] = os.getenv("TEST_DATABASE_USER", "test_user")
    os.environ["DATABASE_PASSWORD"] = os.getenv(
        "TEST_DATABASE_PASSWORD", "test_password"
    )


@pytest.fixture(scope="session")
def test_engine():
    """Create a session-shared SQLAlchemy engine and create model tables."""
    engine = create_engine(_build_test_database_url(), pool_pre_ping=True)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def clean_database(test_engine) -> Generator[None, None, None]:
    """Clean all business tables before each test to ensure isolation."""
    with test_engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE "
                + ", ".join(TABLES_TO_TRUNCATE)
                + " RESTART IDENTITY CASCADE"
            )
        )
    yield


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Provide an HTTP test client to run E2E requests against the app."""
    # Import here to avoid starting app lifespan before configure_test_environment sets env vars
    from src.main import app

    with TestClient(app) as test_client:
        yield test_client
