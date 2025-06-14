# main.py

import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .private import section_key
from .api import bid, product, home, auth, user
from .db.connection import Base, engine, SessionLocal, create_schema_if_not_exists

session = SessionLocal()
create_schema_if_not_exists(session)
session.close()

# logging global configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("LS")
logger.info("Iniciando aplicação FastAPI")

# DB inicialization
Base.metadata.create_all(bind=engine)

# create fastapi app
app = FastAPI()

# routes and static resources
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(bid.router)
app.include_router(product.router)
app.include_router(home.router)
app.include_router(auth.router)
app.include_router(user.router)

# session middleware
app.add_middleware(SessionMiddleware, secret_key=section_key)
