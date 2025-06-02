import sqlite3
import requests
import os
import json
import xml.etree.ElementTree as ET
from pymystem3 import Mystem
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.environ.get("DB_NAME", "news.db")
RSS = json.loads(os.environ.get("RSS", "[]"))
print (RSS)
KEYWORDS = json.loads(os.environ.get("KEYWORDS", "[]"))

def singleton(cls):
    _instances = {}
    def wrapper(*args, **kwargs):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]
    return wrapper

@singleton
class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS news (title TEXT PRIMARY KEY, source TEXT, url TEXT, content TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS rss (url TEXT UNIQUE)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS keywords (word TEXT UNIQUE)")
        self.conn.commit()

    def fetch_rss(self, url):
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
            self.cur.executemany(
                "INSERT OR IGNORE INTO news(title, source, url, content) VALUES (?, ?, ?, ?)", items
            )
            self.conn.commit()
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    def add_rss(self, rss_url):
        self.cur.execute("INSERT OR IGNORE INTO rss(url) VALUES (?)", (rss_url,))
        self.conn.commit()
        self.fetch_rss(rss_url)

    def remove_rss(self, urls):
        for u in urls:
            self.cur.execute("DELETE FROM rss WHERE url = ?", (u,))
            self.cur.execute("DELETE FROM news WHERE source = ?", (u.split('//')[-1].split('/')[0],))
        self.conn.commit()

    def list_rss(self):
        return self.cur.execute("SELECT url FROM rss").fetchall()

    def setup_default_rss(self):
        for url in RSS:
            self.add_rss(url)

    def list_keywords(self):
        return self.cur.execute("SELECT word FROM keywords").fetchall()

    def setup_default_keywords(self):
        self.cur.execute("DELETE FROM keywords")
        self.cur.executemany("INSERT OR IGNORE INTO keywords(word) VALUES (?)", [(w,) for w in KEYWORDS])
        self.conn.commit()

    def add_keywords(self, words):
        self.cur.executemany("INSERT OR IGNORE INTO keywords(word) VALUES (?)", [(w,) for w in words])
        self.conn.commit()

    def remove_keywords(self, words):
        self.cur.executemany("DELETE FROM keywords WHERE word = ?", [(w,) for w in words])
        self.conn.commit()

    def list_news(self):
        keywords_list = [i[0] for i in self.list_keywords()]
        news_list = self.cur.execute("""SELECT * from news""").fetchall()
        str_news =[str(i[0] + "||") for i in news_list]
        m = Mystem()
        counter = 0
        list_of_numbers = []
        for i in m.lemmatize(''.join(str_news)):
            if "||" in i:
                counter +=1
            if i.capitalize() in keywords_list:
                list_of_numbers.append(counter)
        res = []
        for i in list_of_numbers:
            res.append(news_list[i])
        return res
