# app/api/auth.py
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND

from ..db.connection import get_db
from ..models.models import User
from passlib.hash import bcrypt

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login_user(request: Request, name: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == name).first()
    if not user or not bcrypt.verify(password, user.password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Credenciais inválidas"})

    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=HTTP_302_FOUND)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=HTTP_302_FOUND)
