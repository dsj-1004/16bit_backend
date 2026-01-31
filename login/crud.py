from datetime import datetime

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from login.models import Hospital, RefreshToken, User, UserFamily, UserProfile


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, email: str, password_hash: str) -> User:
    user = User(email=email, password_hash=password_hash)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(session: AsyncSession, user: User) -> User:
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def delete_user(session: AsyncSession, user: User) -> None:
    await session.delete(user)
    await session.commit()


async def create_refresh_token(
    session: AsyncSession, user_id: int, token: str, expires_at: datetime
) -> RefreshToken:
    refresh = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
    session.add(refresh)
    await session.commit()
    await session.refresh(refresh)
    return refresh


async def get_refresh_token(session: AsyncSession, token: str) -> RefreshToken | None:
    result = await session.execute(select(RefreshToken).where(RefreshToken.token == token))
    return result.scalar_one_or_none()


async def revoke_refresh_token(session: AsyncSession, token_obj: RefreshToken) -> None:
    await session.execute(
        update(RefreshToken).where(RefreshToken.id == token_obj.id).values(revoked=True)
    )
    await session.commit()


async def get_profile_by_user_id(session: AsyncSession, user_id: int) -> UserProfile | None:
    result = await session.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    return result.scalar_one_or_none()


async def upsert_profile(
    session: AsyncSession,
    user_id: int,
    name: str | None,
    birth_date: str | None,
    gender: str | None,
    height: float | None,
    weight: float | None,
    allergy: dict | None,
    medication: dict | None,
) -> tuple[UserProfile, bool]:
    profile = await get_profile_by_user_id(session, user_id)
    created = False
    if not profile:
        profile = UserProfile(
            user_id=user_id,
            name=name,
            birth_date=birth_date,
            gender=gender,
            height=height,
            weight=weight,
            allergy=allergy,
            medication=medication,
        )
        session.add(profile)
        created = True
    else:
        profile.name = name
        profile.birth_date = birth_date
        profile.gender = gender
        profile.height = height
        profile.weight = weight
        profile.allergy = allergy
        profile.medication = medication
        session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile, created


async def patch_profile(
    session: AsyncSession,
    profile: UserProfile,
    name: str | None,
    birth_date: str | None,
    gender: str | None,
    height: float | None,
    weight: float | None,
    allergy: dict | None,
    medication: dict | None,
) -> UserProfile:
    if name is not None:
        profile.name = name
    if birth_date is not None:
        profile.birth_date = birth_date
    if gender is not None:
        profile.gender = gender
    if height is not None:
        profile.height = height
    if weight is not None:
        profile.weight = weight
    if allergy is not None:
        profile.allergy = allergy
    if medication is not None:
        profile.medication = medication
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile


async def delete_profile(session: AsyncSession, profile: UserProfile) -> None:
    await session.delete(profile)
    await session.commit()


async def list_hospitals(
    session: AsyncSession,
    q: str | None,
    page: int,
    size: int,
) -> tuple[list[Hospital], int]:
    query = select(Hospital)
    count_query = select(func.count(Hospital.id))
    if q:
        like = f"%{q}%"
        query = query.where(Hospital.name.ilike(like))
        count_query = count_query.where(Hospital.name.ilike(like))

    total = (await session.execute(count_query)).scalar_one()
    result = await session.execute(
        query.order_by(Hospital.id).offset((page - 1) * size).limit(size)
    )
    return list(result.scalars().all()), total


async def get_hospital_by_id(session: AsyncSession, hospital_id: int) -> Hospital | None:
    result = await session.execute(select(Hospital).where(Hospital.id == hospital_id))
    return result.scalar_one_or_none()


async def list_family_members(session: AsyncSession, user_id: int) -> list[UserFamily]:
    result = await session.execute(
        select(UserFamily).where(UserFamily.user_id == user_id).order_by(UserFamily.id)
    )
    return list(result.scalars().all())


async def get_family_member(session: AsyncSession, family_id: int) -> UserFamily | None:
    result = await session.execute(select(UserFamily).where(UserFamily.id == family_id))
    return result.scalar_one_or_none()


async def create_family_member(
    session: AsyncSession,
    user_id: int,
    relationship: str,
    name: str | None,
    birth_date: str | None,
    gender: str | None,
    height: float | None,
    weight: float | None,
    allergy: dict | None,
    medication: dict | None,
) -> UserFamily:
    member = UserFamily(
        user_id=user_id,
        relationship=relationship,
        name=name,
        birth_date=birth_date,
        gender=gender,
        height=height,
        weight=weight,
        allergy=allergy,
        medication=medication,
    )
    session.add(member)
    await session.commit()
    await session.refresh(member)
    return member


async def patch_family_member(
    session: AsyncSession,
    member: UserFamily,
    relationship: str | None,
    name: str | None,
    birth_date: str | None,
    gender: str | None,
    height: float | None,
    weight: float | None,
    allergy: dict | None,
    medication: dict | None,
) -> UserFamily:
    if relationship is not None:
        member.relationship = relationship
    if name is not None:
        member.name = name
    if birth_date is not None:
        member.birth_date = birth_date
    if gender is not None:
        member.gender = gender
    if height is not None:
        member.height = height
    if weight is not None:
        member.weight = weight
    if allergy is not None:
        member.allergy = allergy
    if medication is not None:
        member.medication = medication
    session.add(member)
    await session.commit()
    await session.refresh(member)
    return member


async def delete_family_member(session: AsyncSession, member: UserFamily) -> None:
    await session.delete(member)
    await session.commit()
