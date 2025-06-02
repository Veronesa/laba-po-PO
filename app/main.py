from fastapi import FastAPI, Request
from .routers import keywords, news, rss
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3, os, requests, xml.etree.ElementTree as ET

load_dotenv()
DB_NAME = os.environ.get("DB_NAME", "news.db")

def refresh_news():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    rss_urls = [row[0] for row in cur.execute("SELECT url FROM rss").fetchall()]
    for url in rss_urls:
        try:
            resp = requests.get(url, timeout=10)
            tree = ET.fromstring(resp.content)
            items = []
            for item in tree.findall(".//item"):
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                desc = item.findtext("description", "")
                source = url.split("//")[-1].split("/")[0]
                items.append((title, source, link, desc))
            cur.executemany(
                "INSERT OR IGNORE INTO news(title, source, url, content) VALUES (?, ?, ?, ?)", items
            )
            conn.commit()
        except Exception as e:
            print(f"Error: {e}")
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(refresh_news, "interval", minutes=1)
    scheduler.start()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(rss.router)
app.include_router(keywords.router)
app.include_router(news.router)
templates = Jinja2Templates(directory="./app/templates")

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(request=request, name="news.html")
