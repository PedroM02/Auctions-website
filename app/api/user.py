from fastapi import Request, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse

from ..db.connection import get_db
from ..crud.user import *


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/profile", response_class=HTMLResponse)
def profile(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/", status_code=HTTP_302_FOUND)
    user_data = get_user_by_id(db, user_id)
    if not user_data:
        return RedirectResponse("/", status_code=HTTP_302_FOUND)
    
    user_obj = create_user_obj(user_data)

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user_obj
    })
