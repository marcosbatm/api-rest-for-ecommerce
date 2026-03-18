import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.routers.products import products_router
# -------------

from src.database.database import Repository
from src.service.backend import EcommerceBackend

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan_function(app: FastAPI):
    db = Repository(0)  # TODO: use config.
    backend = EcommerceBackend(db)
    app.state.backend = backend
    yield
    # TODO: Close things.


app = FastAPI(lifespan=lifespan_function)

app.include_router(products_router)
