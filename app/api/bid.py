from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND

from ..db.connection import get_db
from ..crud.bid import *
from ..crud.product import get_product
from ..schemas.schemas import BidOut

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/products/{product_id}/bid")
def bid_form(request: Request, product_id: int, db: Session = Depends(get_db)):
    product = get_product(db, product_id)
    if not product:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return templates.TemplateResponse("create_bid.html", {"request": request, "product": product})


@router.post("/products/{product_id}/bid")
def create_bid(
    product_id: int,
    request: Request,
    bid_value: int = Form(...),
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)

    product = get_product(db, product_id)
    if not product or not product.rsa_public_key:
        return RedirectResponse(url="/products", status_code=HTTP_302_FOUND)

    if not bid_value>=product.base_value+1:
        return templates.TemplateResponse("create_bid.html", {
            "request": request,
            "product": product,
            "error": "O valor da licitação tem de ser pelo menos 1€ mais cara que o valor base do produto."
        })
    
    if product.winner_id:
        return templates.TemplateResponse("create_bid.html", {
            "request": request,
            "product": product,
            "error2": "O leilão já terminou"
        })

    create_new_bid(
        db=db,
        product=product,
        user_id=user_id,
        product_id=product_id,
        bid_value=bid_value,
        time_stamp=datetime.now()
    )
    return RedirectResponse(url=f"/products/{product_id}", status_code=HTTP_302_FOUND)
