# main.py
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from .private import section_key
from .api import bid, product, home, auth
from .db.connection import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(bid.router)
app.include_router(product.router)
app.include_router(home.router)
app.include_router(auth.router)
app.add_middleware(SessionMiddleware, secret_key=section_key)
