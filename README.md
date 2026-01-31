# 16bit
16bit 프로젝트

## API (프론트엔드용)

### Base URL
- 기본 prefix: `/api/v1`
- `API_PREFIX` 환경변수로 변경 가능

### 프론트 복붙용 (Base URL + 공통 요청)
```js
const API_BASE = (import.meta?.env?.VITE_API_BASE || "http://127.0.0.1:8000") + "/api/v1";
const req = (path, o = {}) => fetch(API_BASE + path, { method: o.method || "GET", headers: { "Content-Type": "application/json", ...(o.token && { Authorization: `Bearer ${o.token}` }) }, body: o.body && JSON.stringify(o.body) }).then(r => r.ok ? r.json() : r.json().then(e => Promise.reject(e)));
// Auth: 회원가입
const register = (email, password) => req("/auth/register", { method: "POST", body: { email, password } });
// Auth: 로그인
const login = (email, password) => req("/auth/login", { method: "POST", body: { email, password } });
// Auth: 토큰 재발급
const refresh = (refresh_token) => req("/auth/refresh", { method: "POST", body: { refresh_token } });
// Auth: 로그아웃
const logout = (refresh_token) => req("/auth/logout", { method: "POST", body: { refresh_token } });
// User: 내 정보 조회
const me = (token) => req("/me", { token });
// User: 내 정보 수정
const updateMe = (token, body = {}) => req("/me", { method: "PATCH", token, body });
// User: 회원탈퇴
const deleteMe = (token) => req("/me", { method: "DELETE", token });
// Profile: 내 프로필 조회
const getProfile = (token) => req("/me/profile", { token });
// Profile: 내 프로필 생성/전체 갱신
const upsertProfile = (token, body = {}) => req("/me/profile", { method: "PUT", token, body });
// Profile: 내 프로필 부분 수정
const patchProfile = (token, body = {}) => req("/me/profile", { method: "PATCH", token, body });
// Profile: 내 프로필 삭제
const deleteProfile = (token) => req("/me/profile", { method: "DELETE", token });
// Family: 가족 목록
const listFamily = (token) => req("/me/family", { token });
// Family: 가족 추가
const addFamily = (token, body = {}) => req("/me/family", { method: "POST", token, body });
// Family: 가족 부분 수정
const patchFamily = (token, familyId, body = {}) => req(`/me/family/${familyId}`, { method: "PATCH", token, body });
// Family: 가족 삭제
const deleteFamily = (token, familyId) => req(`/me/family/${familyId}`, { method: "DELETE", token });
// Hospital: 병원 목록 조회 (q/page/size)
const listHospitals = (params = {}) => req(`/hospitals${Object.keys(params).length ? `?${new URLSearchParams(params)}` : ""}`);
// Hospital: 병원 단건 조회
const getHospital = (hospitalId) => req(`/hospitals/${hospitalId}`);
```

### Auth
- `POST /auth/register`
  - 요청 Body: `{ "email": "...", "password": "..." }` (회원가입)
  - 응답: `{ "msg": "user created", "id": 1 }`
- `POST /auth/login`
  - 요청 Body: `{ "email": "...", "password": "..." }` (로그인)
  - 응답 예시:
    ```
    { "access_token": "...", "refresh_token": "...", "token_type": "bearer", "expires_in": 1800 }
    ```
- `POST /auth/refresh`
  - 요청 Body: `{ "refresh_token": "..." }` (토큰 재발급)
  - 응답: `/auth/login`과 동일
- `POST /auth/logout`
  - 요청 Body: `{ "refresh_token": "..." }` (로그아웃)
  - 응답: `{ "msg": "logged out" }`

### User (본인만)
- `GET /me`
  - 응답 예시:
    ```
    { "id": 1, "email": "user@example.com", "created_at": "...", "updated_at": "..." }
    ```
- `PATCH /me`
  - 요청 Body: `{ }` (수정 필드 확장 예정)
  - 응답: `GET /me`와 동일
- `DELETE /me`
  - 응답: `204 No Content`

- `GET /users/{id}` (id가 JWT sub와 동일할 때만 허용)
- `PATCH /users/{id}` (id가 JWT sub와 동일할 때만 허용)
- `DELETE /users/{id}` (id가 JWT sub와 동일할 때만 허용)

### User Profile (본인만)
- `GET /me/profile`
- `PUT /me/profile` (없으면 생성, 있으면 전체 갱신)
- `PATCH /me/profile` (부분 수정)
- `DELETE /me/profile`

프로필 요청 Body (모든 필드 선택):
```
{
  "name": "홍길동",
  "birth_date": "1997-10-04",
  "gender": "male",
  "height": 175.0,
  "weight": 70.5,
  "allergy": {
    "has_allergy": "없어요",
    "drug_allergy": ["페니실린계"],
    "medical_allergy": ["라텍스"],
    "food_allergy": ["견과류"],
    "other": ""
  },
  "medication": {
    "taking": "없어요",
    "name": "",
    "dose": "",
    "frequency": "",
    "timing": ""
  }
}
```

### Family (본인만)
- `GET /me/family`
- `POST /me/family`
- `PATCH /me/family/{family_id}`
- `DELETE /me/family/{family_id}`

가족 요청 Body (relationship 필수, 값: child/spouse/father/mother):
```
{
  "relationship": "child",
  "name": "홍길동",
  "birth_date": "2010-05-01",
  "gender": "male",
  "height": 140.5,
  "weight": 35.2,
  "allergy": { "has_allergy": "없어요" },
  "medication": { "taking": "없어요" }
}
```

### Hospital (읽기 전용)
- `GET /hospitals`
  - Query: `q`, `page`, `size`
  - 응답 예시:
    ```
    { "items": [ { "id": 1, "name": "강북삼성병원 응급실", "is_open": true, "distance_km": 1.0, "address": "서울 ...", "er_beds": 2, "operating_rooms": 1 } ], "page": 1, "size": 20, "total": 123 }
    ```
- `GET /hospitals/{hospital_id}`
- `POST/PUT/PATCH/DELETE /hospitals...` -> `405 Method Not Allowed` (읽기 전용)

### 인증 헤더
- `Authorization: Bearer <access_token>`

추가 규칙:
- gender는 `male/female` 또는 `남자/여자` 입력 가능
- relationship는 `child/spouse/father/mother` 또는 `자녀/배우자/부/모` 입력 가능
