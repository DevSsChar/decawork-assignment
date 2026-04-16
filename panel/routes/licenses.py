from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from panel.database import get_state, log_action

router = APIRouter(prefix="/licenses")
templates = Jinja2Templates(directory="panel/templates")

@router.get("", response_class=HTMLResponse)
def list_licenses(request: Request):
    state = get_state()
    users = list(state["users"].values())
    available_licenses = state["available_licenses"]
    return templates.TemplateResponse("licenses.html", {
        "request": request,
        "users": users,
        "available_licenses": available_licenses
    })

@router.post("/assign")
def assign_license(request: Request, email: str = Form(...), license: str = Form(...)):
    state = get_state()
    user = state["users"].get(email)
    
    if not user:
        request.session["flash"] = "User not found"
        request.session["flash_class"] = "flash-error"
    elif license in user["licenses"]:
        request.session["flash"] = "User already has this license"
        request.session["flash_class"] = "flash-error"
    else:
        user["licenses"].append(license)
        log_action("ASSIGN_LICENSE", f"Assigned {license} to {email}")
        request.session["flash"] = f"License {license} assigned successfully"
        request.session["flash_class"] = "flash-success"
        
    return RedirectResponse(url="/licenses", status_code=303)

@router.post("/revoke")
def revoke_license(request: Request, email: str = Form(...), license: str = Form(...)):
    state = get_state()
    user = state["users"].get(email)
    
    if user and license in user["licenses"]:
        user["licenses"].remove(license)
        log_action("REVOKE_LICENSE", f"Revoked {license} from {email}")
        request.session["flash"] = f"License {license} revoked successfully"
        request.session["flash_class"] = "flash-success"
        
    return RedirectResponse(url="/licenses", status_code=303)