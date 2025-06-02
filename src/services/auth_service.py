from passlib.context import CryptContext
from src.repositories.interfaces.users_repository import UserRepositoryInterface

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository

    async def register_user(self, username: str, password: str) -> dict:
        password_hash = pwd_context.hash(password)
        user = await self.user_repository.create(username, password_hash)
        return {"message": f"User {user['username']} successfully registered"}

    async def authenticate_user(self, username: str, password: str) -> str:
        user = await self.user_repository.get_by_username(username)
        if not user:
            raise ValueError("User not found")
        if not pwd_context.verify(password, user["password_hash"]):
            raise ValueError("Incorrect pair login/password")
        return user["username"]
