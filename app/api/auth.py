# app/api/auth.py
from datetime import datetime
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND

from ..db.connection import get_db
from ..crud.user import *
from ..models.models import User
from ..utils.security import verify_username_spaces
from passlib.hash import bcrypt

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register_user(request: Request, name: str = Form(...), password: str = Form(...), email: str = Form(...), birth_date: str = Form(...), db: Session = Depends(get_db)):
    # Verifica se já existe user
    existing_user = get_user_by_username(db, name)
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username já existe"})

    # Valida espaços no username
    if not verify_username_spaces(name):
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username não pode ter espaços"})

    # Hash da password
    hashed_password = bcrypt.hash(password)
    
    # Lida com foto de perfil
    #profile_path = None
    #if profile_picture:
    #    filename = f"profile_{username}_{profile_picture.filename}"
    #    profile_path = os.path.join("app/static/profile_pics", filename)
    #    os.makedirs(os.path.dirname(profile_path), exist_ok=True)
    #    with open(profile_path, "wb") as buffer:
    #        shutil.copyfileobj(profile_picture.file, buffer)

    # Cria e guarda o user
    new_user = User(
        name=name,
        password=hashed_password,
        email=email,
        birthdate=datetime.strptime(birth_date, "%Y-%m-%d"),
        profile_picture=None
        #profile_picture=profile_path
    )
    db.add(new_user)
    db.commit()

    # Sessão iniciada após registo
    request.session["user_id"] = new_user.id
    request.session["username"] = new_user.name
    return RedirectResponse(url="/", status_code=HTTP_302_FOUND)



@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login_user(request: Request, name: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    print(f"Recebido: username={name}, password={password}")

    user = get_user_by_username(db, name)
    if not user or not bcrypt.verify(password, user.password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Credenciais inválidas"})
    if not verify_username_spaces(name):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Username não pode ter espaços"})
    request.session["user_id"] = user.id
    request.session["username"] = user.name 
    return RedirectResponse(url="/", status_code=HTTP_302_FOUND)

@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=HTTP_302_FOUND)
