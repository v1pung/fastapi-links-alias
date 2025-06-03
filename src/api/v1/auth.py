from fastapi import APIRouter, Depends, HTTPException, status
from src.api.v1.dependencies import get_auth_service
from src.services.auth_service import AuthService
from src.schemas.user import RegisterUserRequest, RegisterUserResponse

router = APIRouter()


@router.post("/auth/register", tags=["Auth"], response_model=RegisterUserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: RegisterUserRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Регистрация нового пользователя."""
    try:
        result = await auth_service.register_user(request.username, request.password)
        return result
    except ValueError as e:
        status_code = 409 if "already exists" in str(e).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(e))
