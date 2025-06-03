from typing import List, Optional
from abc import ABC, abstractmethod
from datetime import datetime


class LinkRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, original_url: str, short_url: str, expires_at: datetime, user_id: int) -> dict:
        pass

    @abstractmethod
    async def get_by_short_url(self, short_url: str, user_id: Optional[int] = None) -> Optional[dict]:
        pass

    @abstractmethod
    async def get_all(self, is_active: Optional[bool], limit: int, offset: int, user_id: int) -> List[dict]:
        pass

    @abstractmethod
    async def deactivate(self, short_url: str, user_id: int) -> bool:
        pass

    @abstractmethod
    async def log_click(self, link_id: int) -> None:
        pass

    @abstractmethod
    async def get_stats(self, is_active: Optional[bool], user_id: int) -> List[dict]:
        pass

    @abstractmethod
    async def update_expired_links(self) -> int:
        pass
