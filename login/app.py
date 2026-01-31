import os

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# Load environment variables from .env before importing db/config
load_dotenv(override=True)

from login import db, models
from login.routers import auth_router, family_router, hospitals_router, profiles_router, users_router

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


@app.get("/", response_class=HTMLResponse)
async def dummy_login_page():
    base = api_prefix
    html = """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>JWT Login Test</title>
        <style>
          :root { --bg:#f7f7fb; --card:#fff; --text:#1b1f24; --muted:#6b7280; --accent:#1f7aec; }
          body { margin:0; font-family: system-ui, -apple-system, Segoe UI, sans-serif; background:var(--bg); color:var(--text); }
          .wrap { max-width: 780px; margin: 48px auto; padding: 0 16px; }
          .card { background:var(--card); border-radius:14px; padding:24px; box-shadow:0 8px 24px rgba(0,0,0,.08); }
          h1 { margin:0 0 8px; font-size: 22px; }
          p { margin:0 0 16px; color:var(--muted); }
          label { display:block; font-size: 13px; margin: 10px 0 6px; }
          input, button { width:100%; padding:12px; border-radius:10px; border:1px solid #d5dbe3; }
          button { background:var(--accent); color:#fff; border:none; font-weight:600; cursor:pointer; }
          .row { display:grid; grid-template-columns: 1fr 1fr; gap:12px; }
          pre { white-space: pre-wrap; background:#0f172a; color:#e2e8f0; padding:12px; border-radius:10px; }
        </style>
      </head>
      <body>
        <div class="wrap">
          <div class="card">
            <h1>JWT Login Test</h1>
            <p>Try signup -> login -> /me.</p>

            <div class="row">
              <div>
                <h3>Signup</h3>
                <label>Email</label><input id="su-email" />
                <label>Password</label><input id="su-pass" type="password" />
                <button onclick="signup()">Signup</button>
              </div>
              <div>
                <h3>Login</h3>
                <label>Email</label><input id="li-email" />
                <label>Password</label><input id="li-pass" type="password" />
                <button onclick="login()">Login</button>
              </div>
            </div>

            <h3>Current User (/me)</h3>
            <button onclick="me()">/me</button>
            <h3>Response</h3>
            <pre id="out">ready</pre>
          </div>
        </div>

        <script>
          const base = "__API_PREFIX__";
          let accessToken = "";
          const out = (v) => (document.getElementById("out").textContent = JSON.stringify(v, null, 2));

          async function signup() {
            const body = {
              email: document.getElementById("su-email").value,
              password: document.getElementById("su-pass").value,
            };
            const res = await fetch(base + "/auth/register", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
            out(await res.json());
          }

          async function login() {
            const body = {
              email: document.getElementById("li-email").value,
              password: document.getElementById("li-pass").value
            };
            const res = await fetch(base + "/auth/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
            const data = await res.json();
            accessToken = data.access_token || "";
            out(data);
          }

          async function me() {
            const res = await fetch(base + "/me", { headers: { "Authorization": "Bearer " + accessToken } });
            out(await res.json());
          }
        </script>
      </body>
    </html>
    """
    return html.replace("__API_PREFIX__", base)




if __name__ == "__main__":
    import uvicorn

    uvicorn.run("login.app:app", host="0.0.0.0", port=8000, reload=True)
