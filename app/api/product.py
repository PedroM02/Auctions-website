from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from typing import List
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from ..db.connection import get_db
from ..crud.product import *
from ..schemas.schemas import ProductOut


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/products", response_class=HTMLResponse, response_model=List[ProductOut])
def show_all_products(request: Request, db: Session = Depends(get_db)):
    products = get_all_products(db)
    return templates.TemplateResponse(
        "products.html", 
        {"request": request, "products": products})

@router.get("/products/{product_id}", response_class=HTMLResponse)
def show_product(request: Request, product_id: int, db: Session = Depends(get_db)):
    product = get_product(db, product_id)
    if not product:
        return templates.TemplateResponse(
            "404.html", 
            {"request": request}, status_code=404)
    
    return templates.TemplateResponse(
        "product_detail.html", 
        {"request": request, "product": product})