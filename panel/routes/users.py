from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from panel.database import get_state, log_action
import uuid
from datetime import datetime

router = APIRouter(prefix="/users")
templates = Jinja2Templates(directory="panel/templates")

@router.get("", response_class=HTMLResponse)
def list_users(request: Request):
    state = get_state()
    users = list(state["users"].values())
    return templates.TemplateResponse("users.html", {
        "request": request,
        "users": users
    })

@router.post("/create")
def create_user(
    request: Request,
    email: str = Form(...),
    full_name: str = Form(...),
    department: str = Form(...),
    status: str = Form(...)
):
    state = get_state()
    if email in state["users"]:
        request.session["flash"] = "Email already exists"
        request.session["flash_class"] = "flash-error"
        return RedirectResponse(url="/users", status_code=303)

    state["users"][email] = {
        "id": f"usr_{str(uuid.uuid4())[:6]}",
        "email": email,
        "full_name": full_name,
        "department": department,
        "status": status,
        "password_hash": "hashed_Welcome123",
        "licenses": [],
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "last_login": "Never",
    }
    
    log_action("CREATE_USER", f"Created user {email}")
    request.session["flash"] = f"User {email} created successfully"
    request.session["flash_class"] = "flash-success"
    return RedirectResponse(url="/users", status_code=303)

@router.get("/{email}", response_class=HTMLResponse)
def user_detail(request: Request, email: str):
    state = get_state()
    user = state["users"].get(email)
    if not user:
        request.session["flash"] = "User not found"
        request.session["flash_class"] = "flash-error"
        return RedirectResponse(url="/users", status_code=303)

    return templates.TemplateResponse("user_detail.html", {
        "request": request,
        "user": user
    })

@router.post("/{email}/suspend")
def suspend_user(request: Request, email: str):
    state = get_state()
    user = state["users"].get(email)
    if user:
        if user["status"] == "suspended":
            request.session["flash"] = "User is already suspended"
            request.session["flash_class"] = "flash-error"
        else:
            user["status"] = "suspended"
            log_action("SUSPEND_USER", f"Suspended user {email}")
            request.session["flash"] = f"User {email} suspended successfully"
            request.session["flash_class"] = "flash-success"
    return RedirectResponse(url=f"/users/{email}", status_code=303)

@router.post("/{email}/activate")
def activate_user(request: Request, email: str):
    state = get_state()
    user = state["users"].get(email)
    if user:
        if user["status"] == "active":
            request.session["flash"] = "User is already active"
            request.session["flash_class"] = "flash-error"
        else:
            user["status"] = "active"
            log_action("ACTIVATE_USER", f"Activated user {email}")
            request.session["flash"] = f"User {email} activated successfully"
            request.session["flash_class"] = "flash-success"
    return RedirectResponse(url=f"/users/{email}", status_code=303)