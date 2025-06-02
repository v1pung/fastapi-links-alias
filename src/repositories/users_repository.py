import asyncpg
from src.repositories.interfaces.users_repository import UserRepositoryInterface


class UserRepository(UserRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, username: str, password_hash: str) -> dict:
        async with self.pool.acquire() as conn:
            try:
                record = await conn.fetchrow(
                    """
                    INSERT INTO users (username, password_hash)
                    VALUES ($1, $2)
                    RETURNING id, username, password_hash
                    """,
                    username,
                    password_hash,
                )
                return dict(record)
            except asyncpg.UniqueViolationError:
                raise ValueError(f"User {username} already exists")

    async def get_by_username(self, username: str) -> dict:
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(
                "SELECT id, username, password_hash FROM users WHERE username = $1",
                username,
            )
            return dict(record) if record else None
