from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND
import os
import shutil

from ..db.connection import get_db
from ..crud.product import *
from ..schemas.schemas import ProductOut


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/products/new", response_class=HTMLResponse)
def create_product_form(request: Request):
    if not request.session.get("user_id"):
        return RedirectResponse("/", status_code=HTTP_302_FOUND)
    return templates.TemplateResponse("create_product.html", {"request": request})


@router.post("/products/new")
def create_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    base_value: int = Form(...),
    end_date: str = Form(...),
    photos: List[UploadFile] = File([]),
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/", status_code=HTTP_302_FOUND)

    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    if end_dt > datetime.now() + timedelta(days=30):
        return templates.TemplateResponse("create_product.html", {
            "request": request,
            "error": "Data de fim excede o limite de 30 dias."
        })

    # Guardar fotos
    photo_paths = []
    os.makedirs("static/product_photos", exist_ok=True)
    for photo in photos:
        if photo.filename:
            filename = f"{datetime.now().timestamp()}_{photo.filename}"
            path = os.path.join("static/product_photos", filename)
            with open(path, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)
            photo_paths.append(f"/static/product_photos/{filename}")

    new_product = Product(
        name=name,
        description=description,
        base_value=base_value,
        start_date=datetime.now().strftime("%d-%m-%Y %H:%M"),
        end_date=end_dt,
        vdf_start_time=None,
        vdf_output=None,
        photos=";".join(photo_paths),  # armazenar como texto separado por ponto e vírgula
        seller_id=user_id,
        winner_id=None,
        product_type_id=None
    )
    db.add(new_product)
    db.commit()

    return RedirectResponse("/products", status_code=HTTP_302_FOUND)

@router.get("/products", response_class=HTMLResponse, response_model=List[ProductOut])
def show_all_products(request: Request, db: Session = Depends(get_db)):
    products = get_all_products_with_seller_name(db)

    return templates.TemplateResponse(
        "products.html", 
        {"request": request, "products": products})

@router.get("/products/{product_id}", response_class=HTMLResponse)
def show_product(request: Request, product_id: int, db: Session = Depends(get_db)):
    product = get_product_with_seller_name(db, product_id)[0]
    if not product:
        return templates.TemplateResponse(
            "404.html",
            {"request": request}, status_code=404)
    
    return templates.TemplateResponse(
        "product_detail.html",
        {"request": request, "product": product})

