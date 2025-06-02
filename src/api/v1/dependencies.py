from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from asyncpg.pool import Pool
from typing import Annotated
from src.services.links_service import LinkService
from src.services.auth_service import AuthService
from src.repositories.links_repository import LinkRepository
from src.repositories.users_repository import UserRepository

_app: FastAPI = None


def init_dependencies(app: FastAPI):
    """Инициализирует зависимости, сохраняя ссылку на app."""
    global _app
    _app = app


async def get_pool() -> Pool:
    """Возвращает пул соединений из app.state.pool.

    В текущей реализации это костыль, так как при обращении к оригинальному
    app падает ошибка о циклических импортах. Поэтому инициализируем копию app
    и обращаемся к ней.
    """
    if _app is None or not hasattr(_app.state, "pool"):
        raise RuntimeError("Application pool is not initialized")
    return _app.state.pool


def get_link_repository(pool: Pool = Depends(get_pool)) -> LinkRepository:
    return LinkRepository(pool)


def get_user_repository(pool: Pool = Depends(get_pool)) -> UserRepository:
    return UserRepository(pool)


def get_link_service(
    link_repository: LinkRepository = Depends(get_link_repository),
) -> LinkService:
    return LinkService(link_repository)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repository)


security = HTTPBasic()


async def get_current_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    auth_service: AuthService = Depends(get_auth_service),
) -> str:
    try:
        return await auth_service.authenticate_user(
            credentials.username, credentials.password
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Basic"},
        )
