from sqlalchemy.orm import Session
from ..models.models import User

def get_user_by_username  (db: Session, name: str):
    return db.query(User).filter(User.name == name).first()