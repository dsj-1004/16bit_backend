from pydantic import BaseModel


class UserPublic(BaseModel):
    id: int
    email: str
    created_at: str | None = None
    updated_at: str | None = None


class UserCreate(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserUpdate(BaseModel):
    pass


class UserProfilePublic(BaseModel):
    user_id: int
    name: str | None = None
    birth_date: str | None = None
    gender: str | None = None
    height: float | None = None
    weight: float | None = None
    allergy: dict | None = None
    medication: dict | None = None
    updated_at: str | None = None


class UserProfileUpsert(BaseModel):
    name: str | None = None
    birth_date: str | None = None
    gender: str | None = None
    height: float | None = None
    weight: float | None = None
    allergy: dict | None = None
    medication: dict | None = None


class UserProfilePatch(BaseModel):
    name: str | None = None
    birth_date: str | None = None
    gender: str | None = None
    height: float | None = None
    weight: float | None = None
    allergy: dict | None = None
    medication: dict | None = None


class HospitalPublic(BaseModel):
    id: int
    name: str
    is_open: bool
    distance_km: float | None = None
    address: str | None = None
    er_beds: int | None = None
    operating_rooms: int | None = None


class HospitalList(BaseModel):
    items: list[HospitalPublic]
    page: int
    size: int
    total: int


class UserFamilyPublic(BaseModel):
    id: int
    user_id: int
    relationship: str
    name: str | None = None
    birth_date: str | None = None
    gender: str | None = None
    height: float | None = None
    weight: float | None = None
    allergy: dict | None = None
    medication: dict | None = None
    updated_at: str | None = None


class UserFamilyCreate(BaseModel):
    relationship: str
    name: str | None = None
    birth_date: str | None = None
    gender: str | None = None
    height: float | None = None
    weight: float | None = None
    allergy: dict | None = None
    medication: dict | None = None


class UserFamilyPatch(BaseModel):
    relationship: str | None = None
    name: str | None = None
    birth_date: str | None = None
    gender: str | None = None
    height: float | None = None
    weight: float | None = None
    allergy: dict | None = None
    medication: dict | None = None
