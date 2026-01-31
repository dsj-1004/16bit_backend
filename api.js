const API_BASE = (import.meta?.env?.VITE_API_BASE || "http://127.0.0.1:8000") + "/api/v1";
const req = (path, o = {}) => fetch(API_BASE + path, { method: o.method || "GET", headers: { "Content-Type": "application/json", ...(o.token && { Authorization: `Bearer ${o.token}` }) }, body: o.body && JSON.stringify(o.body) }).then(r => r.ok ? r.json() : r.json().then(e => Promise.reject(e)));
export const api = {
  // Auth: 회원가입
  register: (email, password) => req("/auth/register", { method: "POST", body: { email, password } }),
  // Auth: 로그인
  login: (email, password) => req("/auth/login", { method: "POST", body: { email, password } }),
  // Auth: 토큰 재발급
  refresh: (refresh_token) => req("/auth/refresh", { method: "POST", body: { refresh_token } }),
  // Auth: 로그아웃
  logout: (refresh_token) => req("/auth/logout", { method: "POST", body: { refresh_token } }),
  // User: 내 정보 조회
  me: (token) => req("/me", { token }),
  // User: 내 정보 수정
  updateMe: (token, body = {}) => req("/me", { method: "PATCH", token, body }),
  // User: 회원탈퇴
  deleteMe: (token) => req("/me", { method: "DELETE", token }),
  // Profile: 내 프로필 조회
  getProfile: (token) => req("/me/profile", { token }),
  // Profile: 내 프로필 생성/전체 갱신
  upsertProfile: (token, body = {}) => req("/me/profile", { method: "PUT", token, body }),
  // Profile: 내 프로필 부분 수정
  patchProfile: (token, body = {}) => req("/me/profile", { method: "PATCH", token, body }),
  // Profile: 내 프로필 삭제
  deleteProfile: (token) => req("/me/profile", { method: "DELETE", token }),
  // Family: 가족 목록
  listFamily: (token) => req("/me/family", { token }),
  // Family: 가족 추가
  addFamily: (token, body = {}) => req("/me/family", { method: "POST", token, body }),
  // Family: 가족 부분 수정
  patchFamily: (token, familyId, body = {}) => req(`/me/family/${familyId}`, { method: "PATCH", token, body }),
  // Family: 가족 삭제
  deleteFamily: (token, familyId) => req(`/me/family/${familyId}`, { method: "DELETE", token }),
  // Hospital: 병원 목록 조회 (q/page/size)
  listHospitals: (params = {}) => req(`/hospitals${Object.keys(params).length ? `?${new URLSearchParams(params)}` : ""}`),
  // Hospital: 병원 단건 조회
  getHospital: (hospitalId) => req(`/hospitals/${hospitalId}`),
  // AutoCall: 자동 연결 트리거
  triggerAutoCall: (token, hospital_ids = []) => req("/auto-call/trigger", { method: "POST", token, body: { hospital_ids } }),
};
export { API_BASE, req };
