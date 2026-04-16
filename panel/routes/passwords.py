from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from panel.database import get_state, log_action
import random

router = APIRouter()
templates = Jinja2Templates(directory="panel/templates")

@router.get("/reset-password", response_class=HTMLResponse)
def get_reset_password(request: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request})

@router.post("/reset-password")
def post_reset_password(request: Request, email: str = Form(...)):
    state = get_state()
    user = state["users"].get(email)
    
    if not user:
        request.session["flash"] = "User not found"
        request.session["flash_class"] = "flash-error"
    else:
        temp_pass = f"Temp{random.randint(1000, 9999)}!"
        user["password_hash"] = f"hashed_{temp_pass}"
        log_action("RESET_PASSWORD", f"Password reset for {email}")
        request.session["flash"] = f"Password reset successful! New temporary password: {temp_pass}"
        request.session["flash_class"] = "flash-success"
        
    # As per PRD, returning the same page with the result flash message
    return templates.TemplateResponse("reset_password.html", {"request": request})