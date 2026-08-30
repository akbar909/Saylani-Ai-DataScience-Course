from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.core.model_registry import ModelRegistry
from app.core.security import decode_access_token
from app.models.user import User
from app.services.fraud import FraudService

security = HTTPBearer(auto_error=False)


def get_model_registry(request: Request) -> ModelRegistry:
    return request.app.state.model_registry


async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        user_id = decode_access_token(credentials.credentials)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_fraud_service(request: Request) -> FraudService:
    return request.app.state.fraud_service
