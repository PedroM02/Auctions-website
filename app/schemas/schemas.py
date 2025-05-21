from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class BidOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    time_stamp: datetime
    encrypted_value: str
    commitment_hash: str

    class Config:
        orm_mode = True

class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    base_value: int
    #start_value: Optional[datetime] = None se for nullable
    start_date: datetime
    end_date: datetime
    vdf_start_time: Optional[datetime] = None
    vdf_output: Optional[str] = None
    photos: Optional[List[str]] = None
    winner_id: Optional[int] = None
    product_type_id: int
    bids: List[BidOut]

    class Config:
        orm_mode = True
    
#class UserOut(BaseModel):
