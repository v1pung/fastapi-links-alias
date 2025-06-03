from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.links_service import LinkService
from src.services.auth_service import AuthService
from src.repositories.links_repository import LinkRepository
from src.repositories.users_repository import UserRepository
from src.db.database import get_async_session


def get_link_repository(session: AsyncSession = Depends(get_async_session)) -> LinkRepository:
    return LinkRepository(session)


def get_user_repository(session: AsyncSession = Depends(get_async_session)) -> UserRepository:
    return UserRepository(session)


def get_link_service(link_repository: LinkRepository = Depends(get_link_repository)) -> LinkService:
    return LinkService(link_repository)


def get_auth_service(user_repository: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repository)


security = HTTPBasic()


async def get_current_user(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)],
        auth_service: AuthService = Depends(get_auth_service)
) -> str:
    try:
        return await auth_service.authenticate_user(credentials.username, credentials.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Basic"},
        )
