from sqlalchemy.orm import Session
from ..models.models import Product

def get_all_products(db: Session):
    return db.query(Product).all()

def get_product(db: Session, product_id: int):
    return db.get(Product, product_id)
