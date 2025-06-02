from fastapi import APIRouter, Depends, HTTPException
from src.api.v1.dependencies import get_auth_service
from src.services.auth_service import AuthService
from src.schemas.user import RegisterUserRequest, RegisterUserResponse

router = APIRouter()


@router.post("/auth/register", tags=["Auth"], response_model=RegisterUserResponse)
async def register_user(
    request: RegisterUserRequest, auth_service: AuthService = Depends(get_auth_service)
):
    """Регистрация нового пользователя."""
    try:
        result = await auth_service.register_user(request.username, request.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
