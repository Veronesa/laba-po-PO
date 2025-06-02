from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from ..dependencies import get_session
from pydantic import BaseModel
from DataCollection.collection import Database

router = APIRouter(prefix="/news")
templates = Jinja2Templates(directory="./app/templates")

@router.get("")
def get_news(request: Request, session: Database = Depends(get_session)):
    news = session.list_news()
    return templates.TemplateResponse(request=request, name="news.html", context={
        "news": [{"id":news.index(i),"title":i[0], "source": i[1], "url":i[2]} for i in news],
        "keywords": session.list_keywords()
    })
