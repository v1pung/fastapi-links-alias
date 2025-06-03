from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from src.repositories.interfaces.users_repository import UserRepositoryInterface
from src.models import User


class UserRepository(UserRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, username: str, password_hash: str) -> dict:
        user = User(username=username, password_hash=password_hash)
        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user.__dict__
        except IntegrityError:
            await self.session.rollback()
            raise ValueError(f"User {username} already exists")

    async def get_by_username(self, username: str) -> dict:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        user = result.scalars().first()
        return user.__dict__ if user else None
