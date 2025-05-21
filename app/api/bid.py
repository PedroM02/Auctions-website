from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db.connection import get_db
from ..crud.bid import *
from ..schemas.schemas import BidOut
from typing import List

router = APIRouter()

@router.get("/bids", response_model=List[BidOut])
def read_all_bids(db: Session = Depends(get_db)):
    return get_all_bids(db)
