import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from src.repositories.interfaces.links_repository import LinkRepositoryInterface
from src.core.config import settings


class LinkService:
    def __init__(self, link_repository: LinkRepositoryInterface):
        self.link_repository = link_repository

    async def create_short_url(self, original_url: str) -> str:
        short_url = str(uuid.uuid4())[: settings.SHORT_URL_LENGTH]
        expires_at = datetime.now() + timedelta(days=settings.DEFAULT_LINK_EXPIRY_DAYS)
        link = await self.link_repository.create(original_url, short_url, expires_at)
        return f"http://localhost:8000/{link['short_url']}"

    async def get_link_by_short_url(self, short_url: str) -> dict:
        link = await self.link_repository.get_by_short_url(short_url)
        if not link:
            raise ValueError("Link not found")
        if not link["is_active"]:
            raise ValueError("Link is deactivated")
        if link["expires_at"] and link["expires_at"] < datetime.now():
            raise ValueError("Link has expired")
        return link

    async def get_all_links(
        self, is_active: Optional[bool], limit: int, offset: int
    ) -> List[dict]:
        return await self.link_repository.get_all(is_active, limit, offset)

    async def deactivate_link(self, short_url: str) -> str:
        success = await self.link_repository.deactivate(short_url)
        if not success:
            raise ValueError("Link not found or already deactivated")
        return f"Link {short_url} deactivated"

    async def log_click(self, short_url: str) -> None:
        link = await self.link_repository.get_by_short_url(short_url)
        if not link:
            raise ValueError("Link not found")
        await self.link_repository.log_click(link["id"])

    async def get_stats(self, is_active: Optional[bool]) -> List[dict]:
        stats = await self.link_repository.get_stats(is_active)
        return [
            {
                "link": f"http://localhost:8000/{stat['short_url']}",
                "orig_link": stat["original_url"],
                "last_hour_clicks": stat["last_hour_clicks"],
                "last_day_clicks": stat["last_day_clicks"],
            }
            for stat in stats
        ]
