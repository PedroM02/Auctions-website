from sqlalchemy.orm import Session
from ..models.models import Bid

def get_all_bids(session: Session):
    return session.query(Bid).all()
