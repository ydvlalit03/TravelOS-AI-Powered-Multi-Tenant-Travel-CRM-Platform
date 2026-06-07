"""Authentication & onboarding endpoints."""
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant, get_current_user, get_user_by_email
from app.core.db import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.utils import random_suffix, slugify
from app.models.tenant import Tenant, User, UserRole
from app.schemas.auth import (
    LoginRequest,
    MeResponse,
    OnboardingUpdate,
    RefreshRequest,
    SignupRequest,
    TenantOut,
    TokenPair,
    UserOut,
)

router = APIRouter(prefix="/auth", tags=["auth"])


async def _unique_slug(db: AsyncSession, name: str) -> str:
    base = slugify(name)
    slug = base
    while True:
        exists = await db.execute(select(Tenant.id).where(Tenant.slug == slug))
        if exists.first() is None:
            return slug
        slug = f"{base}-{random_suffix()}"


@router.post("/signup", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    """Create a new agency workspace (tenant) and its owner user."""
    if await get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    tenant = Tenant(name=payload.agency_name, slug=await _unique_slug(db, payload.agency_name))
    db.add(tenant)
    await db.flush()  # populate tenant.id

    user = User(
        tenant_id=tenant.id,
        email=payload.email.lower(),
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=UserRole.owner,
    )
    db.add(user)
    await db.flush()

    return TokenPair(
        access_token=create_access_token(str(user.id), str(tenant.id)),
        refresh_token=create_refresh_token(str(user.id), str(tenant.id)),
    )


@router.post("/login", response_model=TokenPair)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    user = await get_user_by_email(db, payload.email)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    return TokenPair(
        access_token=create_access_token(str(user.id), str(user.tenant_id)),
        refresh_token=create_refresh_token(str(user.id), str(user.tenant_id)),
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    try:
        claims = decode_token(payload.refresh_token)
        if claims.get("type") != "refresh":
            raise ValueError
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    user = await db.get(User, claims["sub"])
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    return TokenPair(
        access_token=create_access_token(str(user.id), str(user.tenant_id)),
        refresh_token=create_refresh_token(str(user.id), str(user.tenant_id)),
    )


@router.get("/me", response_model=MeResponse)
async def me(
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
) -> MeResponse:
    return MeResponse(user=UserOut.model_validate(user), tenant=TenantOut.model_validate(tenant))


@router.patch("/onboarding", response_model=TenantOut)
async def update_onboarding(
    payload: OnboardingUpdate,
    tenant: Tenant = Depends(get_current_tenant),
) -> TenantOut:
    tenant.onboarding_completed = payload.completed
    return TenantOut.model_validate(tenant)
