from sqlalchemy.orm import Session
from ..models.models import Product
from .user import get_user_by_id

def get_all_products(db: Session):
    return db.query(Product).all()

def get_product(db: Session, product_id: int):
    return db.get(Product, product_id)

def get_product_with_seller_name(db: Session, product_id: int):
    product = db.get(Product, product_id)
    product_data = []
    seller = get_user_by_id(db, product.seller_id)
    product_data.append({
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "base_value": product.base_value,
        "start_date": product.start_date,
        "end_date": product.end_date,
        "photos": product.photos or "",
        "seller_name": seller.name if seller else "Desconhecido"
    })
    
    return product_data


def get_all_products_with_seller_name(db: Session):
    products = db.query(Product).all()
    product_data = []
    for product in products:
        seller = get_user_by_id(db, product.seller_id)
        product_data.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "base_value": product.base_value,
            "start_date": product.start_date,
            "end_date": product.end_date,
            "photos": product.photos or "",
            "seller_name": seller.name if seller else "Desconhecido"
        })
    
    return product_data