from fastapi import APIRouter, Request, Depends, Body, HTTPException
from fastapi.templating import Jinja2Templates
from ..dependencies import get_session
from pydantic import BaseModel
from DataCollection.collection import Database
import urllib.parse

class ListItem(BaseModel):
    list: list[str]


router = APIRouter(prefix="/keywords")
templates = Jinja2Templates(directory="./app/templates")

@router.get("")
def get_keywords(request: Request, session: Database = Depends(get_session)):
    kws = session.list_keywords()
    return templates.TemplateResponse(request=request, name="keywords.html", context={"list": [{"id": i, "word": w[0]} for i, w in enumerate(kws)]})

@router.put("")
def add_keywords(item: ListItem, session : Database = Depends(get_session)):
    if item.list:
        session.add_keywords(item.list)
        

@router.delete("")
def delete_keywords(item: ListItem, session: Database = Depends(get_session)):
    if item.list:
        session.remove_keywords(item.list)

@router.post("")
def reset_keywords(request: Request, word: str = Body(...), session: Database = Depends(get_session)): 
    session.add_keywords([urllib.parse.unquote(word.encode("utf-8")).split("=")[1]])
    kws = session.list_keywords()
    return templates.TemplateResponse(request=request, name="keywords.html", context={"list": [{"id": i, "word": w[0]} for i, w in enumerate(kws)]})

@router.delete("")
def delete_keywords(
    data: ListItem = Body(...), 
    session: Database = Depends(get_session)
):
    try:
        if data.list:
            session.remove_keywords(data.list)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(500, str(e))
