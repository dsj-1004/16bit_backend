from fastapi import APIRouter, Depends, HTTPException, status

from login import crud, schemas
from login.deps import get_session
from login.security import get_current_user

router = APIRouter(tags=["profiles"])

GENDER_MAP = {
    "남자": "male",
    "여자": "female",
    "male": "male",
    "female": "female",
}


def _normalize_gender(value: str | None) -> str | None:
    if value is None:
        return None
    mapped = GENDER_MAP.get(value)
    if not mapped:
        raise HTTPException(status_code=400, detail="invalid gender")
    return mapped


@router.get("/me/profile", response_model=schemas.UserProfilePublic)
async def get_profile(user=Depends(get_current_user), session=Depends(get_session)):
    profile = await crud.get_profile_by_user_id(session, user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="profile not found")
    return schemas.UserProfilePublic(
        user_id=profile.user_id,
        name=profile.name,
        birth_date=profile.birth_date,
        gender=profile.gender,
        height=profile.height,
        weight=profile.weight,
        allergy=profile.allergy,
        medication=profile.medication,
        updated_at=profile.updated_at.isoformat(),
    )


@router.put("/me/profile", response_model=schemas.UserProfilePublic)
async def upsert_profile(
    payload: schemas.UserProfileUpsert,
    user=Depends(get_current_user),
    session=Depends(get_session),
):
    profile, created = await crud.upsert_profile(
        session,
        user.id,
        payload.name,
        payload.birth_date,
        _normalize_gender(payload.gender),
        payload.height,
        payload.weight,
        payload.allergy,
        payload.medication,
    )
    return schemas.UserProfilePublic(
        user_id=profile.user_id,
        name=profile.name,
        birth_date=profile.birth_date,
        gender=profile.gender,
        height=profile.height,
        weight=profile.weight,
        allergy=profile.allergy,
        medication=profile.medication,
        updated_at=profile.updated_at.isoformat(),
    )


@router.patch("/me/profile", response_model=schemas.UserProfilePublic)
async def patch_profile(
    payload: schemas.UserProfilePatch,
    user=Depends(get_current_user),
    session=Depends(get_session),
):
    profile = await crud.get_profile_by_user_id(session, user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="profile not found")
    profile = await crud.patch_profile(
        session,
        profile,
        payload.name,
        payload.birth_date,
        _normalize_gender(payload.gender),
        payload.height,
        payload.weight,
        payload.allergy,
        payload.medication,
    )
    return schemas.UserProfilePublic(
        user_id=profile.user_id,
        name=profile.name,
        birth_date=profile.birth_date,
        gender=profile.gender,
        height=profile.height,
        weight=profile.weight,
        allergy=profile.allergy,
        medication=profile.medication,
        updated_at=profile.updated_at.isoformat(),
    )


@router.delete("/me/profile", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(user=Depends(get_current_user), session=Depends(get_session)):
    profile = await crud.get_profile_by_user_id(session, user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="profile not found")
    await crud.delete_profile(session, profile)
    return None
