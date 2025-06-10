# app/db/connection.py

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from ..private import db_pass


DATABASE_URL = f"postgresql://postgres:{db_pass}@host.docker.internal:5432/postgres?options=-csearch_path%3DsiteLeiloes"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()