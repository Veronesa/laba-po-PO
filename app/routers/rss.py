from fastapi import APIRouter, Request, Depends, Body, status
from fastapi.templating import Jinja2Templates
from ..dependencies import get_session
from pydantic import BaseModel
from DataCollection.collection import Database
from fastapi.responses import RedirectResponse
import urllib.parse

class Item(BaseModel):
    url: str

class ListItem(BaseModel):
    list: list[str]

router = APIRouter(prefix="/rss")
templates = Jinja2Templates(directory="./app/templates")

@router.get("")
def get_rss(request: Request, session: Database = Depends(get_session)):
    rss_list = session.list_rss()
    return templates.TemplateResponse(request=request, name="rss.html", context={"list": [{"id": i, "rss": r[0]} for i, r in enumerate(rss_list)]})

@router.put("")
def add_rss(item: Item, session: Database = Depends(get_session)):
    session.add_rss(item.url)

@router.delete("")
def delete_rss(list_item: ListItem, session: Database = Depends(get_session)):
    session.remove_rss(list_item.list)

@router.post("")
def reset_rss(request: Request, word: str = Body(...), session: Database = Depends(get_session)):
    session.add_rss(urllib.parse.unquote(word.encode("utf-8")).split("=")[1])
    return RedirectResponse(url="/rss", status_code=status.HTTP_303_SEE_OTHER)
    
    # kws = session.list_keywords()
    # return templates.TemplateResponse(request=request, name="keywords.html", context={"list": [{"id": i, "word": w[0]} for i, w in enumerate(kws)]})