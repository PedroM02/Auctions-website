from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND

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
    end_time: str = Form(None),
    photos: List[UploadFile] = File([]),
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/", status_code=HTTP_302_FOUND)

    end_dt = parse_end_dt(end_date, end_time)

    is_max_product_end_dt, max_weeks = maximum_product_end_dt(end_dt)
    is_min_product_end_dt, min_weeks, start_dt = minimum_product_end_dt(end_dt)

    if is_max_product_end_dt:
        return templates.TemplateResponse("create_product.html", {
            "request": request,
            "error": f"The auction must have less than {max_weeks}"
        })
    
    if is_min_product_end_dt:
        return templates.TemplateResponse("create_product.html", {
            "request": request,
            "error": f"The auction must have at least {min_weeks}"
        })
    
    create_new_product(user_id, name, description, base_value, end_dt, photos, db, start_dt)
    db.commit()

    return RedirectResponse("/products?finished=false", status_code=HTTP_302_FOUND)

@router.get("/products", response_class=HTMLResponse, response_model=List[ProductOut])
def show_all_products(request: Request, q: str = "", finished: bool = False, db: Session = Depends(get_db)):
    products, f = parse_query_and_products(db, q, finished)
    return templates.TemplateResponse(
        "products.html",
        {"request": request, "products": products, "query": q, "finished": f})

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
