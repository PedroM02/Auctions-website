# app/api/auth.py


from fastapi import APIRouter, Request, Form, Depends, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND
from passlib.hash import bcrypt

from ..db.connection import get_db
from ..crud.user import *
from ..models.models import User
from ..utils.security import verify_username_spaces


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register_user(request: Request, name: str = Form(...), password: str = Form(...), email: str = Form(...), birth_date: str = Form(...), profile_picture: UploadFile = File(None), db: Session = Depends(get_db)):
    # verify if the username is already taken
    existing_user = get_user_by_username(db, name)
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already exists"})

    if verify_duplicate_email(db, email):
        return templates.TemplateResponse("register.html", {"request": request, "error": "Email already being used"})

    # verify if there are no spaces in the username
    if not verify_username_spaces(name):
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username can't have spaces"})
    
    new_user = create_user(name, email, password, birth_date, profile_picture)

    db.add(new_user)
    db.commit()

    # log in after register
    request.session["user_id"] = new_user.id
    request.session["username"] = new_user.name
    return RedirectResponse(url="/", status_code=HTTP_302_FOUND)


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login_user(request: Request, name: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):

    user = get_user_by_username(db, name)
    if not user or not verify_password(password, user):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Login failed. Invalid credentials provided"})
    if not verify_username_spaces(name):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Login failed. Username can't have spaces"})
    request.session["user_id"] = user.id
    request.session["username"] = user.name 
    return RedirectResponse(url="/", status_code=HTTP_302_FOUND)

@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=HTTP_302_FOUND)
