import asyncpg
from typing import List, Optional
from datetime import datetime
from src.repositories.interfaces.links_repository import LinkRepositoryInterface


class LinkRepository(LinkRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(
        self, original_url: str, short_url: str, expires_at: datetime
    ) -> dict:
        async with self.pool.acquire() as conn:
            try:
                record = await conn.fetchrow(
                    """
                    INSERT INTO links (original_url, short_url, expires_at, click_count)
                    VALUES ($1, $2, $3, 0)
                    RETURNING id, original_url, short_url, is_active, created_at, expires_at, click_count
                    """,
                    original_url,
                    short_url,
                    expires_at,
                )
                return dict(record)
            except asyncpg.UniqueViolationError:
                raise ValueError("Short URL already exists")

    async def get_by_short_url(self, short_url: str) -> dict:
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                SELECT id, original_url, short_url, is_active, created_at, expires_at, click_count
                FROM links
                WHERE short_url = $1
                """,
                short_url,
            )
            return dict(record) if record else None

    async def get_all(
        self, is_active: Optional[bool], limit: int, offset: int
    ) -> List[dict]:
        query = """
            SELECT id, original_url, short_url, is_active, created_at, expires_at, click_count
            FROM links
            WHERE ($1::boolean IS NULL OR is_active = $1)
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
        """
        async with self.pool.acquire() as conn:
            records = await conn.fetch(query, is_active, limit, offset)
            return [dict(record) for record in records]

    async def deactivate(self, short_url: str) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE links SET is_active = FALSE WHERE short_url = $1 AND is_active = TRUE",
                short_url,
            )
            return result != "UPDATE 0"

    async def log_click(self, link_id: int) -> None:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("INSERT INTO clicks (link_id) VALUES ($1)", link_id)
                await conn.execute(
                    "UPDATE links SET click_count = click_count + 1 WHERE id = $1",
                    link_id,
                )

    async def get_stats(self, is_active: Optional[bool]) -> List[dict]:
        query = """
            SELECT
                l.short_url,
                l.original_url,
                COUNT(CASE WHEN c.clicked_at >= NOW() - INTERVAL '1 hour' THEN 1 END) AS last_hour_clicks,
                COUNT(CASE WHEN c.clicked_at >= NOW() - INTERVAL '24 hours' THEN 1 END) AS last_day_clicks
            FROM links l
            LEFT JOIN clicks c ON l.id = c.link_id
            WHERE ($1::boolean IS NULL OR l.is_active = $1)
            GROUP BY l.id, l.short_url, l.original_url
            ORDER BY last_day_clicks DESC, last_hour_clicks DESC
        """
        async with self.pool.acquire() as conn:
            records = await conn.fetch(query, is_active)
            return [dict(record) for record in records]
