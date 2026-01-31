from fastapi import APIRouter, Depends, HTTPException, status

from login import crud, schemas
from login.deps import get_session
from login.security import get_current_user

router = APIRouter(tags=["family"])

RELATIONSHIP_MAP = {
    "자녀": "child",
    "배우자": "spouse",
    "부": "father",
    "모": "mother",
    "child": "child",
    "spouse": "spouse",
    "father": "father",
    "mother": "mother",
}


def _normalize_relationship(value: str) -> str:
    mapped = RELATIONSHIP_MAP.get(value)
    if not mapped:
        raise HTTPException(status_code=400, detail="invalid relationship")
    return mapped


def _normalize_gender(value: str | None) -> str | None:
    if value is None:
        return None
    if value == "남자":
        return "male"
    if value == "여자":
        return "female"
    if value in {"male", "female"}:
        return value
    raise HTTPException(status_code=400, detail="invalid gender")


@router.get("/me/family", response_model=list[schemas.UserFamilyPublic])
async def list_family(user=Depends(get_current_user), session=Depends(get_session)):
    items = await crud.list_family_members(session, user.id)
    return [
        schemas.UserFamilyPublic(
            id=i.id,
            user_id=i.user_id,
            relationship=i.relationship,
            name=i.name,
            birth_date=i.birth_date,
            gender=i.gender,
            height=i.height,
            weight=i.weight,
            allergy=i.allergy,
            medication=i.medication,
            updated_at=i.updated_at.isoformat(),
        )
        for i in items
    ]


@router.post("/me/family", response_model=schemas.UserFamilyPublic, status_code=status.HTTP_201_CREATED)
async def create_family(
    payload: schemas.UserFamilyCreate, user=Depends(get_current_user), session=Depends(get_session)
):
    relationship = _normalize_relationship(payload.relationship)
    member = await crud.create_family_member(
        session,
        user.id,
        relationship,
        payload.name,
        payload.birth_date,
        _normalize_gender(payload.gender),
        payload.height,
        payload.weight,
        payload.allergy,
        payload.medication,
    )
    return schemas.UserFamilyPublic(
        id=member.id,
        user_id=member.user_id,
        relationship=member.relationship,
        name=member.name,
        birth_date=member.birth_date,
        gender=member.gender,
        height=member.height,
        weight=member.weight,
        allergy=member.allergy,
        medication=member.medication,
        updated_at=member.updated_at.isoformat(),
    )


@router.patch("/me/family/{family_id}", response_model=schemas.UserFamilyPublic)
async def patch_family(
    family_id: int,
    payload: schemas.UserFamilyPatch,
    user=Depends(get_current_user),
    session=Depends(get_session),
):
    member = await crud.get_family_member(session, family_id)
    if not member or member.user_id != user.id:
        raise HTTPException(status_code=404, detail="family member not found")
    relationship = None
    if payload.relationship is not None:
        relationship = _normalize_relationship(payload.relationship)
    member = await crud.patch_family_member(
        session,
        member,
        relationship,
        payload.name,
        payload.birth_date,
        _normalize_gender(payload.gender),
        payload.height,
        payload.weight,
        payload.allergy,
        payload.medication,
    )
    return schemas.UserFamilyPublic(
        id=member.id,
        user_id=member.user_id,
        relationship=member.relationship,
        name=member.name,
        birth_date=member.birth_date,
        gender=member.gender,
        height=member.height,
        weight=member.weight,
        allergy=member.allergy,
        medication=member.medication,
        updated_at=member.updated_at.isoformat(),
    )


@router.delete("/me/family/{family_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_family(
    family_id: int, user=Depends(get_current_user), session=Depends(get_session)
):
    member = await crud.get_family_member(session, family_id)
    if not member or member.user_id != user.id:
        raise HTTPException(status_code=404, detail="family member not found")
    await crud.delete_family_member(session, member)
    return None
