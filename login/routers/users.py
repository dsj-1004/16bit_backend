from fastapi import APIRouter, Depends, HTTPException, status

from login import crud, schemas
from login.deps import get_session
from login.security import get_current_user

router = APIRouter(tags=["users"])


@router.get("/me", response_model=schemas.UserPublic)
async def me(user=Depends(get_current_user), session=Depends(get_session)):
    db_user = await crud.get_user_by_id(session, user.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="user not found")
    return schemas.UserPublic(
        id=db_user.id,
        email=db_user.email,
        created_at=db_user.created_at.isoformat(),
        updated_at=db_user.updated_at.isoformat(),
    )


@router.patch("/me", response_model=schemas.UserPublic)
async def update_me(
    payload: schemas.UserUpdate, user=Depends(get_current_user), session=Depends(get_session)
):
    db_user = await crud.get_user_by_id(session, user.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="user not found")
    updated = await crud.update_user(session, db_user)
    return schemas.UserPublic(
        id=updated.id,
        email=updated.email,
        created_at=updated.created_at.isoformat(),
        updated_at=updated.updated_at.isoformat(),
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(user=Depends(get_current_user), session=Depends(get_session)):
    db_user = await crud.get_user_by_id(session, user.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="user not found")
    await crud.delete_user(session, db_user)
    return None


@router.get("/users/{user_id}", response_model=schemas.UserPublic)
async def get_user_by_id(
    user_id: int, user=Depends(get_current_user), session=Depends(get_session)
):
    if user_id != user.id:
        raise HTTPException(status_code=403, detail="forbidden")
    return await me(user, session)


@router.patch("/users/{user_id}", response_model=schemas.UserPublic)
async def patch_user_by_id(
    user_id: int,
    payload: schemas.UserUpdate,
    user=Depends(get_current_user),
    session=Depends(get_session),
):
    if user_id != user.id:
        raise HTTPException(status_code=403, detail="forbidden")
    return await update_me(payload, user, session)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(
    user_id: int, user=Depends(get_current_user), session=Depends(get_session)
):
    if user_id != user.id:
        raise HTTPException(status_code=403, detail="forbidden")
    return await delete_me(user, session)
