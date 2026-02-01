from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
import secrets

from login import crud, schemas
from login.deps import get_session
from login.security import (
    ACCESS_EXPIRE_MIN,
    REFRESH_EXPIRE_DAYS,
    create_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(tags=["auth"])


def build_token_response(access_token: str, refresh_token: str) -> schemas.TokenResponse:
    return schemas.TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_EXPIRE_MIN * 60,
    )


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register(payload: schemas.UserCreate, session=Depends(get_session)):
    existing = await crud.get_user_by_email(session, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="email already registered")

    user = await crud.create_user(session, payload.email, hash_password(payload.password))
    return {"msg": "user created", "id": user.id}


@router.post("/auth/login", response_model=schemas.TokenResponse)
async def login(payload: schemas.UserLogin, session=Depends(get_session)):
    user = await crud.get_user_by_email(session, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")

    access_token = create_access_token(user.id)
    refresh_token = secrets.token_urlsafe(48)
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS)
    await crud.create_refresh_token(session, user.id, refresh_token, expires_at)

    return build_token_response(access_token, refresh_token)


@router.post("/auth/refresh", response_model=schemas.TokenResponse)
async def refresh(req: schemas.RefreshRequest, session=Depends(get_session)):
    token_obj = await crud.get_refresh_token(session, req.refresh_token)
    if not token_obj or token_obj.revoked or token_obj.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="invalid refresh token")

    await crud.revoke_refresh_token(session, token_obj)
    new_refresh = secrets.token_urlsafe(48)
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS)
    await crud.create_refresh_token(session, token_obj.user_id, new_refresh, expires_at)

    access = create_access_token(token_obj.user_id)
    return build_token_response(access, new_refresh)


@router.post("/auth/logout")
async def logout(req: schemas.RefreshRequest, session=Depends(get_session)):
    token_obj = await crud.get_refresh_token(session, req.refresh_token)
    if token_obj:
        await crud.revoke_refresh_token(session, token_obj)
    return {"msg": "logged out"}
