from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.db.database import create_pool, init_db
from src.api.v1.dependencies import init_dependencies
from src.api.v1 import main_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    app.state.pool = await create_pool()
    await init_db(app.state.pool)
    init_dependencies(app)
    yield
    if app.state.pool:
        await app.state.pool.close()


app = FastAPI(
    title="URL Alias Service",
    version="1.0.0",
    description="API for short URLs creation and management",
    lifespan=lifespan,
)

app.include_router(main_router)
