from abc import ABC, abstractmethod


class UserRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, username: str, password_hash: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: str) -> dict:
        raise NotImplementedError
