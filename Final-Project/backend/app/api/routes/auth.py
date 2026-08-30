from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.security import create_access_token, hash_password, verify_password
from app.models.organization import Organization
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserRead


router = APIRouter(prefix="/auth", tags=["auth"])


def user_read(user: User) -> UserRead:
    return UserRead(id=str(user.id), email=user.email, organization_id=user.organization_id, role=user.role)


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserCreate, request: Request) -> TokenResponse:
    if not hasattr(request.app.state, "database_client"):
        raise HTTPException(status_code=503, detail="Database is not initialized")
    if await User.find_one(User.email == payload.email) is not None:
        raise HTTPException(status_code=409, detail="Email is already registered")
    organization = await Organization(name=payload.organization_name, plan="starter").insert()
    user = await User(
        organization_id=str(organization.id),
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role="owner",
    ).insert()
    return TokenResponse(access_token=create_access_token(str(user.id)), user=user_read(user))


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, request: Request) -> TokenResponse:
    if not hasattr(request.app.state, "database_client"):
        raise HTTPException(status_code=503, detail="Database is not initialized")
    user = await User.find_one(User.email == payload.email)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(str(user.id)), user=user_read(user))


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return user_read(current_user)
