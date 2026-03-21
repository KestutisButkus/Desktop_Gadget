import re, feedparser
from config import LINES_NEWS

def _get_rss_news(url, limit=LINES_NEWS):
    try:
        f = feedparser.parse(url)
        res = []
        for e in f.entries[:limit]:
            img = ""
            m = e.get("media_content", e.get("enclosures", []))
            if m: img = m[0].get("url", m[0].get("href", ""))
            if not img:
                found = re.search(r'src="([^"]+)"', e.get("summary") or e.get("description") or "")
                if found: img = found.group(1)
            res.append((e.title, e.link, img))
        return res if res else [("Srautas tuščias", "", "")]
    except Exception as e:
        return [(f"Ryšio klaida: {str(e)[:15]}", "", "")]

def get_15min_news(): return _get_rss_news("https://www.15min.lt/rss")
def get_lrt_news():   return _get_rss_news("https://www.lrt.lt/?rss")
def get_delfi_news(): return _get_rss_news("https://feed.delfi.lt/v2/channel/global-lt?format=rss")
def get_vz_news():    return _get_rss_news("https://www.vz.lt/rss")

