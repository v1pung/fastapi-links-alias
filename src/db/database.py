import asyncpg
from src.core.config import settings


async def create_pool():
    """Создает пул подключений к базе данных."""
    return await asyncpg.create_pool(settings.DB_URL, min_size=1, max_size=10)


async def init_db(pool: asyncpg.Pool):
    """Инициализирует таблицы links, users и clicks, если они не существуют."""
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS links (
                id SERIAL PRIMARY KEY,
                original_url TEXT NOT NULL,
                short_url VARCHAR(10) UNIQUE NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                click_count INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS clicks (
                id SERIAL PRIMARY KEY,
                link_id INTEGER REFERENCES links(id) ON DELETE CASCADE,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
