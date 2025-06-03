# app/finalise_products.py
from celery_worker import celery_app
from .db.connection import SessionLocal
from .crud.product import finalize_expired_auctions

@celery_app.task
def run_finalize_auctions():
    db = SessionLocal()
    try:
        print("🔍 A verificar leilões expirados...")
        finalize_expired_auctions(db)
    finally:
        db.close()
