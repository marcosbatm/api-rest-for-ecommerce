import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from src.models.errors import ErrorResponse
from src.routers.products import products_router
# -------------

from src.database.database import Repository
from src.service.backend import EcommerceBackend

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan_function(app: FastAPI):
    db = Repository(None)  # TODO: use config.
    backend = EcommerceBackend(db)
    app.state.backend = backend
    yield
    # TODO: Close things.


app = FastAPI(lifespan=lifespan_function)


@app.exception_handler(RequestValidationError)
async def request_validation_to_400_handler(
    request: Request, exc: RequestValidationError
):
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
app.openapi = custom_openapi
