# main.py
from fastapi import FastAPI

from .api import bid, product, home
from .db.connection import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(bid.router)
app.include_router(product.router)
app.include_router(home.router)
