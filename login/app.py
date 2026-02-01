import os

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# Load environment variables from .env before importing db/config
load_dotenv(override=True)

from login import db, models
from login.routers import (
    auth_router,
    autocall_router,
    family_router,
    hospitals_router,
    profiles_router,
    users_router,
)

app = FastAPI(title="FastAPI JWT Auth - Async SQLAlchemy + Refresh Tokens")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    # DB schema is managed manually via db_init.sql
    pass

def normalize_prefix(prefix: str) -> str:
    p = prefix.strip()
    if not p or p == "/":
        return ""
    if not p.startswith("/"):
        p = "/" + p
    return p.rstrip("/")


api_prefix = normalize_prefix(os.getenv("API_PREFIX", "/api/v1"))

app.include_router(auth_router, prefix=api_prefix)
app.include_router(users_router, prefix=api_prefix)
app.include_router(profiles_router, prefix=api_prefix)
app.include_router(hospitals_router, prefix=api_prefix)
app.include_router(family_router, prefix=api_prefix)
app.include_router(autocall_router, prefix=api_prefix)


@app.get("/", response_class=HTMLResponse)
async def dummy_login_page():
    base = api_prefix
    html = """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>API Smoke Test</title>
        <style>
          :root { --bg:#f7f7fb; --card:#fff; --text:#1b1f24; --muted:#6b7280; --accent:#1f7aec; }
          body { margin:0; font-family: system-ui, -apple-system, Segoe UI, sans-serif; background:var(--bg); color:var(--text); }
          .wrap { max-width: 980px; margin: 32px auto; padding: 0 16px; }
          .card { background:var(--card); border-radius:14px; padding:20px; box-shadow:0 8px 24px rgba(0,0,0,.08); }
          h1 { margin:0 0 8px; font-size: 22px; }
          h3 { margin:16px 0 8px; }
          p { margin:0 0 12px; color:var(--muted); }
          label { display:block; font-size: 12px; margin: 8px 0 4px; }
          input, select, textarea, button { width:100%; padding:10px; border-radius:10px; border:1px solid #d5dbe3; }
          textarea { min-height: 70px; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
          button { background:var(--accent); color:#fff; border:none; font-weight:600; cursor:pointer; margin-top:6px; }
          .row { display:grid; grid-template-columns: 1fr 1fr; gap:12px; }
          .grid { display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; }
          .buttons { display:grid; grid-template-columns: repeat(2, 1fr); gap:8px; }
          pre { white-space: pre-wrap; background:#0f172a; color:#e2e8f0; padding:12px; border-radius:10px; }
        </style>
      </head>
      <body>
        <div class="wrap">
          <div class="card">
            <h1>API Smoke Test</h1>
            <p>Signup -> Login -> CRUD test</p>

            <div class="row">
              <div>
                <h3>Signup</h3>
                <label>Email</label><input id="su-email" value="test@example.com" />
                <label>Password</label><input id="su-pass" type="password" value="pass1234" />
                <button onclick="signup()">Signup</button>
              </div>
              <div>
                <h3>Login</h3>
                <label>Email</label><input id="li-email" value="test@example.com" />
                <label>Password</label><input id="li-pass" type="password" value="pass1234" />
                <button onclick="login()">Login</button>
              </div>
            </div>

            <div class="grid">
              <div>
                <h3>User</h3>
                <div class="buttons">
                  <button onclick="me()">GET /me</button>
                  <button onclick="meDelete()">DELETE /me</button>
                </div>
              </div>
              <div>
                <h3>Profile</h3>
                <label>Name</label><input id="p-name" value="Test User" />
                <label>Birth Date</label><input id="p-birth" value="1997-10-04" />
                <label>Gender</label>
                <select id="p-gender">
                  <option value="male">male</option>
                  <option value="female">female</option>
                </select>
                <label>Height</label><input id="p-height" value="175.0" />
                <label>Weight</label><input id="p-weight" value="70.5" />
                <label>Allergy (JSON)</label><textarea id="p-allergy">{"has_allergy":"no"}</textarea>
                <label>Medication (JSON)</label><textarea id="p-med">{"taking":"no"}</textarea>
                <div class="buttons">
                  <button onclick="profileUpsert()">PUT /me/profile</button>
                  <button onclick="profileGet()">GET /me/profile</button>
                  <button onclick="profilePatch()">PATCH /me/profile</button>
                  <button onclick="profileDelete()">DELETE /me/profile</button>
                </div>
              </div>
              <div>
                <h3>Family</h3>
                <label>Family ID</label><input id="f-id" value="" placeholder="for PATCH/DELETE" />
                <label>Relationship</label>
                <select id="f-rel">
                  <option value="child">child</option>
                  <option value="spouse">spouse</option>
                  <option value="father">father</option>
                  <option value="mother">mother</option>
                </select>
                <label>Name</label><input id="f-name" value="Test Family" />
                <label>Birth Date</label><input id="f-birth" value="2010-05-01" />
                <label>Gender</label>
                <select id="f-gender">
                  <option value="male">male</option>
                  <option value="female">female</option>
                </select>
                <label>Height</label><input id="f-height" value="140.5" />
                <label>Weight</label><input id="f-weight" value="35.2" />
                <label>Allergy (JSON)</label><textarea id="f-allergy">{"has_allergy":"no"}</textarea>
                <label>Medication (JSON)</label><textarea id="f-med">{"taking":"no"}</textarea>
                <div class="buttons">
                  <button onclick="familyAdd()">POST /me/family</button>
                  <button onclick="familyList()">GET /me/family</button>
                  <button onclick="familyPatch()">PATCH /me/family/{id}</button>
                  <button onclick="familyDelete()">DELETE /me/family/{id}</button>
                </div>
              </div>
            </div>

            <div class="row">
              <div>
                <h3>Hospitals (read-only)</h3>
                <label>Query (q)</label><input id="h-q" value="" />
                <button onclick="hospitals()">GET /hospitals</button>
              </div>
              <div>
                <h3>Hospital detail</h3>
                <label>Hospital ID</label><input id="h-id" value="1" />
                <button onclick="hospitalGet()">GET /hospitals/{id}</button>
              </div>
            </div>

            <h3>Response</h3>
            <pre id="out">ready</pre>
          </div>
        </div>

        <script>
          const base = "__API_PREFIX__";
          let accessToken = "";
          const out = (v) => (document.getElementById("out").textContent = JSON.stringify(v, null, 2));

          async function req(path, method = "GET", body) {
            const headers = { "Content-Type": "application/json" };
            if (accessToken) headers.Authorization = "Bearer " + accessToken;
            const res = await fetch(base + path, { method, headers, body: body ? JSON.stringify(body) : undefined });
            const data = await res.json().catch(() => ({}));
            if (!res.ok) throw data;
            return data;
          }

          async function signup() {
            const body = { email: su("email"), password: su("pass") };
            out(await req("/auth/register", "POST", body));
          }

          async function login() {
            const body = { email: li("email"), password: li("pass") };
            const data = await req("/auth/login", "POST", body);
            accessToken = data.access_token || "";
            out(data);
          }

          async function me() { out(await req("/me")); }
          async function meDelete() { out(await req("/me", "DELETE")); }

          async function profileUpsert() {
            const body = profilePayload();
            out(await req("/me/profile", "PUT", body));
          }
          async function profileGet() { out(await req("/me/profile")); }
          async function profilePatch() {
            const body = profilePayload();
            out(await req("/me/profile", "PATCH", body));
          }
          async function profileDelete() { out(await req("/me/profile", "DELETE")); }

          async function familyAdd() {
            const body = familyPayload();
            out(await req("/me/family", "POST", body));
          }
          async function familyList() { out(await req("/me/family")); }
          async function familyPatch() {
            const id = gv("f-id");
            out(await req(`/me/family/${id}`, "PATCH", familyPayload()));
          }
          async function familyDelete() {
            const id = gv("f-id");
            out(await req(`/me/family/${id}`, "DELETE"));
          }

          async function hospitals() {
            const q = gv("h-q");
            const qs = q ? `?q=${encodeURIComponent(q)}` : "";
            out(await req(`/hospitals${qs}`));
          }
          async function hospitalGet() { out(await req(`/hospitals/${gv("h-id")}`)); }

          function profilePayload() {
            return {
              name: gv("p-name"),
              birth_date: gv("p-birth"),
              gender: gv("p-gender"),
              height: num("p-height"),
              weight: num("p-weight"),
              allergy: parseJson("p-allergy"),
              medication: parseJson("p-med"),
            };
          }
          function familyPayload() {
            return {
              relationship: gv("f-rel"),
              name: gv("f-name"),
              birth_date: gv("f-birth"),
              gender: gv("f-gender"),
              height: num("f-height"),
              weight: num("f-weight"),
              allergy: parseJson("f-allergy"),
              medication: parseJson("f-med"),
            };
          }

          function parseJson(id) {
            try { return JSON.parse(gv(id) || "{}"); } catch { return {}; }
          }
          function num(id) { const v = gv(id); return v === "" ? null : Number(v); }
          function su(field) { return gv(`su-${field}`); }
          function li(field) { return gv(`li-${field}`); }
          function gv(id) { return document.getElementById(id).value; }
        </script>
      </body>
    </html>
    """
    return html.replace("__API_PREFIX__", base)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("login.app:app", host="0.0.0.0", port=8000, reload=True)
