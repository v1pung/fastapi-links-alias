from src.api.v1.auth import router as auth_router
from src.api.v1.links import router as users_router
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

main_router = APIRouter()
main_router.include_router(auth_router)
main_router.include_router(users_router)


@main_router.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")
