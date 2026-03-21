import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from src.models.errors import ErrorResponse
from src.routers.products import products_router
from src.routers.carts import carts_router
# -------------

from src.config_app import Config
from src.config_logging import configure_logging
from src.repository.repository import Repository
from src.repository.repositoryDatabase import RepositoryDatabase
from src.repository.repositoryMemory import RepositoryMemory
from src.service.backend import EcommerceBackend


configure_logging()

logger = logging.getLogger(__name__)


def build_repository(config: Config) -> Repository:
    logger.info("Initializing repository for environment=%s", config.environment)
    if config.is_memory_db():
        logger.warning("Using in-memory repository (MOCK_DB=true)")
        return RepositoryMemory()

    logger.info(
        "Using database repository (host=%s port=%s db=%s)",
        config.database_host,
        config.database_port,
        config.database_name,
    )
    return RepositoryDatabase(config)


@asynccontextmanager
async def lifespan_function(app: FastAPI):
    logger.info("Starting application lifespan")
    config = Config()
    repo = build_repository(config)
    backend = EcommerceBackend(repo)
    app.state.backend = backend
    logger.info("Application startup completed")
    yield
    logger.info("Application shutdown completed")
    # TODO: Close things.


app = FastAPI(lifespan=lifespan_function)


@app.exception_handler(RequestValidationError)
async def request_validation_to_400_handler(
    request: Request, exc: RequestValidationError
):
    logger.warning("Request validation error at %s: %s", request.url, exc)
    payload = ErrorResponse(
        type="about:blank",
        title="Bad Request",
        status=status.HTTP_400_BAD_REQUEST,
        detail=str(exc),
        instance=str(request.url),
    ).model_dump()
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=payload,
        media_type="application/problem+json",
    )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Quitar 422 de todas las operaciones
    for _, path_item in schema.get("paths", {}).items():
        for _, operation in path_item.items():
            if isinstance(operation, dict):
                operation.get("responses", {}).pop("422", None)

    app.openapi_schema = schema
    return app.openapi_schema


app.include_router(products_router)
app.include_router(carts_router)
app.openapi = custom_openapi
