from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime


class LinkRepositoryInterface(ABC):
    @abstractmethod
    async def create(
        self, original_url: str, short_url: str, expires_at: datetime
    ) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def get_by_short_url(self, short_url: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def get_all(
        self, is_active: Optional[bool], limit: int, offset: int
    ) -> List[dict]:
        raise NotImplementedError

    @abstractmethod
    async def deactivate(self, short_url: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def log_click(self, link_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_stats(self, is_active: Optional[bool]) -> List[dict]:
        raise NotImplementedError
