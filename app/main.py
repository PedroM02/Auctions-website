# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from .private import section_key
from .api import bid, product, home, auth, user
from .db.connection import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(bid.router)
app.include_router(product.router)
app.include_router(home.router)
app.include_router(auth.router)
app.include_router(user.router)
app.add_middleware(SessionMiddleware, secret_key=section_key)
