import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from src.repositories.interfaces.links_repository import LinkRepositoryInterface
from src.core.config import settings


class LinkService:
    def __init__(self, link_repository: LinkRepositoryInterface):
        self.link_repository = link_repository

    async def _validate_link(
        self, link: Optional[dict], short_url: str,
        user: Optional[dict] = None
    ) -> dict:
        """Валидирует ссылку, проверяя ее существование, срок действия и статус активности."""
        if not link:
            message = f"Public link not found: {short_url}" if user is None \
                else f"Link not found: {short_url} for user {user['username']}"
            raise ValueError("Link not found")
        if link["expires_at"] < datetime.now():
            await self.update_expired_links()
            raise ValueError("Link has expired")
        if not link["is_active"]:
            message = f"Public link is inactive: {short_url}" if user is None \
                else f"Link is inactive: {short_url} for user {user['username']}"
            raise ValueError("Link is inactive")
        return link

    async def get_by_short_url(self, short_url: str, user: dict) -> dict:
        link = await self.link_repository.get_by_short_url(short_url, user["id"])
        return await self._validate_link(link, short_url, user)

    async def get_by_short_url_public(self, short_url: str) -> dict:
        link = await self.link_repository.get_by_short_url(short_url)
        return await self._validate_link(link, short_url)

    async def create_short_url(self, original_url: str, user: dict) -> str:
        short_url = str(uuid.uuid4())[: settings.SHORT_URL_LENGTH]
        expires_at = datetime.now() + timedelta(days=settings.DEFAULT_LINK_EXPIRY_DAYS)
        link = await self.link_repository.create(original_url, short_url, expires_at, user["id"])
        return f"http://localhost:8000/{link['short_url']}"

    async def get_all_links(
        self, is_active: Optional[bool], limit: int, offset: int, user: dict
    ) -> List[dict]:
        await self.link_repository.update_expired_links()

        links = await self.link_repository.get_all(is_active, limit, offset, user["id"])
        return [
            {
                **link,
                "short_url": f"http://localhost:8000/{link['short_url']}"
            }
            for link in links
        ]

    async def deactivate_link(self, short_url: str, user: dict) -> str:
        success = await self.link_repository.deactivate(short_url, user["id"])
        if not success:
            raise ValueError("Link not found or already deactivated")
        return f"Link {short_url} deactivated"

    async def log_click(self, short_url: str) -> None:
        link = await self.get_by_short_url_public(short_url)
        await self.link_repository.log_click(link["id"])

    async def get_stats(self, is_active: Optional[bool], user: dict) -> List[dict]:
        await self.link_repository.update_expired_links()
        stats = await self.link_repository.get_stats(is_active, user["id"])
        return [
            {
                "link": f"http://localhost:8000/{stat['short_url']}",
                "orig_link": stat["original_url"],
                "last_hour_clicks": stat["last_hour_clicks"],
                "last_day_clicks": stat["last_day_clicks"],
            }
            for stat in stats
        ]

    async def update_expired_links(self) -> None:
        await self.link_repository.update_expired_links()
