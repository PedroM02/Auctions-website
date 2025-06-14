# app/db/connection.py

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

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

def create_schema_if_not_exists(session):
    session.execute(text("CREATE SCHEMA IF NOT EXISTS siteLeiloes"))
    session.commit()