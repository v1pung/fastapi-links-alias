from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.db.database import init_db, engine
from src.api.v1 import main_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    await init_db()
    yield
    await engine.dispose()


app = FastAPI(
    title="URL Alias Service",
    version="1.0.0",
    description="API for short URLs creation and management",
    lifespan=lifespan,
)

app.include_router(main_router)
