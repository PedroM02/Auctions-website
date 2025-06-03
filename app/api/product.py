from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta, time
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND

from zoneinfo import ZoneInfo
from ..db.connection import get_db
from ..crud.product import *
from ..schemas.schemas import ProductOut


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
lisbon_tz = ZoneInfo("Europe/Lisbon")
utc_tz = ZoneInfo("UTC")


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
    end_time: str = Form(None),
    photos: List[UploadFile] = File([]),
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/", status_code=HTTP_302_FOUND)

    # Parse end date
    date_part = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Parse hour and minute if provided, otherwise default to 18:00
    if end_time:
        hour, minute = map(int, end_time.split(":"))
    else:
        hour, minute = 18, 0  # default to 18h00

    end_dt = datetime.combine(date_part, time(hour, minute))
    if end_dt.now(tz=utc_tz) > datetime.now(tz=lisbon_tz) + timedelta(days=30):
        return templates.TemplateResponse("create_product.html", {
            "request": request,
            "error": "Data de fim excede o limite de 30 dias."
        })
    
    create_new_product(user_id, name, description, base_value, end_dt, photos, db)
    db.commit()

    return RedirectResponse("/products", status_code=HTTP_302_FOUND)

@router.get("/products", response_class=HTMLResponse, response_model=List[ProductOut])
def show_all_products(request: Request, q: str = "", finished: bool = False, db: Session = Depends(get_db)):
    products = get_all_products(db)
    query = db.query(Product)
    if q:
        query = query.filter(
            (Product.name.ilike(f"%{q}%")) |
            (Product.description.ilike(f"%{q}%"))
        )
    now = datetime.now(tz=lisbon_tz)
    print(Product.end_date)
    if finished:
        query = query.filter(Product.end_date <= now)
    else:
        query = query.filter(Product.end_date > now)

    products = query.all()
    return templates.TemplateResponse(
        "products.html",
        {"request": request, "products": products, "query": q, "finished": finished, "now": now})

@router.get("/products/{product_id}", response_class=HTMLResponse)
def show_product(request: Request, product_id: int, q: str = "", finished: bool = False, db: Session = Depends(get_db)):
    product = get_complete_product(db, product_id)[0]
    if not product:
        return templates.TemplateResponse(
            "404.html",
            {"request": request}, status_code=404)
    
    return templates.TemplateResponse(
        "product_detail.html",
        {"request": request, "product": product, "query": q, "finished": finished})

