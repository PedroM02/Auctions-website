# main.py
from fastapi import FastAPI
from api.routes_user import router as user_router

app = FastAPI()
app.include_router(user_router, prefix="/users")