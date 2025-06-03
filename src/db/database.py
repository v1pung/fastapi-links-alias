from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.core.config import settings
from src.db import Base  # Импортируем Base
from src.models import User, Link, Click  # Импортируем модели для создания таблиц

engine = create_async_engine(
    settings.DB_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=True if settings.MODE == "dev" else False,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncSession:
    """Предоставляет асинхронную сессию для транзакций."""
    async with async_session() as session:
        yield session


async def init_db():
    """Инициализирует таблицы в базе данных."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
