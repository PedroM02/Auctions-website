# app/crud/user.py

import os
import shutil

from sqlalchemy.orm import Session
from fastapi import UploadFile
from passlib.hash import bcrypt
from datetime import datetime

from ..models.models import User


def get_user_by_username(db: Session, name: str):
    return db.query(User).filter(User.name == name).first()

def get_user_by_id(db: Session, id: int):
    return db.query(User).filter(User.id == id).first()

def verify_duplicate_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def delete_user(db, user):
    if user:
        db.delete(user)
        db.commit()
        # Remove o ficheiro se não for a imagem default
        if not user.profile_picture.endswith("default-avatar-profile-icon.jpg"):
            try:
                os.remove("." + user.profile_picture)
            except FileNotFoundError:
                pass

def create_user_obj(user_data: User):
    return {
        "name": user_data.name,
        "email": user_data.email,
        "birth_date": user_data.birthdate.strftime("%Y-%m-%d"),
        "profile_picture": user_data.profile_picture
    }

def create_user(name: str, email: str, password: str, birth_date: str, profile_picture: UploadFile):
    # protect the password
    hashed_password = bcrypt.hash(password)
    
    # path photo saving
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    static_dir = os.path.join(project_root, "static", "profile_pictures")
    os.makedirs(static_dir, exist_ok=True)

    profile_path = None
    if profile_picture:
        filename = f"profile_{name}_{profile_picture.filename}"
        full_path = os.path.join(static_dir, filename)

        with open(full_path, "wb") as buffer:
            shutil.copyfileobj(profile_picture.file, buffer)

        profile_path = f"/static/profile_pictures/{filename}"

    # create and save the new User
    return User(
        name=name,
        password=hashed_password,
        email=email,
        birthdate=datetime.strptime(birth_date, "%Y-%m-%d"),
        profile_picture=profile_path
    )