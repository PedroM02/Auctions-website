from sqlalchemy.orm import Session
from ..models.models import User
import os

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