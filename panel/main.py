from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates

from panel.routes import users, passwords, licenses
from panel.database import get_state

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="super_secret_session_key")

app.mount("/static", StaticFiles(directory="panel/static"), name="static")

templates = Jinja2Templates(directory="panel/templates")

app.include_router(users.router)
app.include_router(passwords.router)
app.include_router(licenses.router)

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    state = get_state()
    users_data = state["users"].values()
    
    total_users = len(users_data)
    active_users = sum(1 for u in users_data if u["status"] == "active")
    suspended_users = sum(1 for u in users_data if u["status"] == "suspended")
    
    audit_log = list(reversed(state["audit_log"]))[:5]
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "total_users": total_users,
        "active_users": active_users,
        "suspended_users": suspended_users,
        "audit_log": audit_log,
    })