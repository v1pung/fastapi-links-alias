from typing import Optional, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasicCredentials
from src.api.v1.dependencies import get_link_service, get_current_user
from src.services.links_service import LinkService
from src.schemas.link import (
    CreateShortUrlRequest,
    CreateShortUrlResponse,
    DeactivateLinkResponse,
    LinkResponse,
)
from src.schemas.stats import StatsResponse

router = APIRouter()


@router.get("/links", tags=["Private"], response_model=list[LinkResponse])
async def get_links(
    creds: Annotated[HTTPBasicCredentials, Depends(get_current_user)],
    is_active: Optional[bool] = None,
    limit: int = 10,
    offset: int = 0,
    link_service: LinkService = Depends(get_link_service),
):
    """Получение списка ссылок с пагинацией и фильтрацией по активным ссылкам."""
    try:
        links = await link_service.get_all_links(is_active, limit, offset)
        return [LinkResponse.model_validate(link) for link in links]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/create_short_url", tags=["Private"], response_model=CreateShortUrlResponse
)
async def create_short_url(
    creds: Annotated[HTTPBasicCredentials, Depends(get_current_user)],
    request: CreateShortUrlRequest,
    link_service: LinkService = Depends(get_link_service),
):
    """Создание короткой ссылки."""
    try:
        short_url = await link_service.create_short_url(str(request.original_url))
        return {"short_url": short_url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/deactivate/{short_url}", tags=["Private"], response_model=DeactivateLinkResponse
)
async def deactivate_url(
    creds: Annotated[HTTPBasicCredentials, Depends(get_current_user)],
    short_url: str,
    link_service: LinkService = Depends(get_link_service),
):
    """Деактивация короткой ссылки."""
    try:
        message = await link_service.deactivate_link(short_url)
        return {"message": message}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stats", tags=["Private"], response_model=list[StatsResponse])
async def get_all_stats(
    creds: Annotated[HTTPBasicCredentials, Depends(get_current_user)],
    is_active: Optional[bool] = None,
    link_service: LinkService = Depends(get_link_service),
):
    """Получение статистики по всем коротким ссылкам с сортировкой по количеству переходов за день."""
    try:
        return await link_service.get_stats(is_active)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{short_url}", tags=["Public"])
async def redirect_url(
    short_url: str,
    request: Request,
    link_service: LinkService = Depends(get_link_service),
):
    """Редирект на оригинальную ссылку"""
    try:
        link = await link_service.get_link_by_short_url(short_url)
        await link_service.log_click(short_url)

        # Избежание ошибки CORS при обращении с /docs
        if "application/json" in request.headers.get("accept", ""):
            return {"original_url": link["original_url"]}
        return RedirectResponse(
            url=link["original_url"], status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )
    except ValueError as e:
        status_code = 404 if "not found" in str(e).lower() else 403
        raise HTTPException(status_code=status_code, detail=str(e))
