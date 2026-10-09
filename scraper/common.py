import json, re, time, unicodedata, html, os, urllib.request, urllib.error
from datetime import date, datetime

UA = "Mozilla/5.0 (compatible; BarrysConcertAgenda/1.0; +https://github.com/bzwijgers/Concerten)"
FIXTURES = os.environ.get("FIXTURES")  # map url -> local file for offline tests

NL_MONTHS = {"januari":1,"jan":1,"februari":2,"feb":2,"maart":3,"mrt":3,"april":4,"apr":4,"mei":5,"juni":6,"jun":6,
             "juli":7,"jul":7,"augustus":8,"aug":8,"september":9,"sep":9,"sept":9,"oktober":10,"okt":10,"november":11,"nov":11,"december":12,"dec":12}

def fetch(url, tries=3, timeout=40, headers=None):
    if FIXTURES:
        m = json.load(open(FIXTURES))
        if url in m:
            return open(m[url], encoding="utf-8", errors="replace").read()
        raise RuntimeError("no fixture for " + url)
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "nl,en;q=0.8", **(headers or {})})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                return raw.decode(r.headers.get_content_charset() or "utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (403, 404, 410):
                break
            time.sleep(3 * (i + 1))
        except Exception as e:
            last = e
            time.sleep(3 * (i + 1))
    raise RuntimeError(f"fetch failed {url}: {last}")

def fetch_json(url, **kw):
    return json.loads(fetch(url, **kw))

def clean(s):
    return re.sub(r"\s+", " ", html.unescape(html.unescape(s or ""))).strip()

def parse_nl_date(s):
    """'26 september 2027', 'vr 9 okt 2026', 'vr 09-okt-2026' -> 'YYYY-MM-DD'"""
    s = clean(s).lower()
    m = re.search(r"(\d{1,2})[\s\-./]+([a-z]+)\.?[\s\-./]+(\d{4})", s)
    if m and m.group(2) in NL_MONTHS:
        return f"{int(m.group(3)):04d}-{NL_MONTHS[m.group(2)]:02d}-{int(m.group(1)):02d}"
    return None

def ld_events(htmltext):
    """All schema.org Event objects in ld+json blocks."""
    out = []
    def walk(o):
        if isinstance(o, dict):
            t = o.get("@type")
            ts = t if isinstance(t, list) else [t]
            if any(isinstance(x, str) and x.endswith("Event") for x in ts):
                out.append(o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', htmltext, re.S):
        try:
            walk(json.loads(m.group(1)))
        except Exception:
            pass
    return out

def ev(venue, d, title, url, time_="", room="", sold=False, club=False, extra=None):
    e = {"v": venue, "d": d, "n": clean(title), "u": url, "t": time_, "r": clean(room), "s": bool(sold), "c": bool(club)}
    return e

def sold_from_offers(o):
    offers = o.get("offers")
    offs = offers if isinstance(offers, list) else [offers] if offers else []
    for x in offs:
        a = str((x or {}).get("availability", ""))
        if "SoldOut" in a or "OutOfStock" in a:
            return True
    return False

def cancelled(o):
    return "Cancel" in str(o.get("eventStatus", ""))

def split_dt(s):
    """'2026-12-17T20:30' or '2026-10-12 20:00:00' -> (date, 'HH:MM')"""
    m = re.match(r"(\d{4}-\d\d-\d\d)[T ](\d\d:\d\d)", s or "")
    if m:
        return m.group(1), m.group(2)
    m = re.match(r"(\d{4}-\d\d-\d\d)", s or "")
    return (m.group(1), "") if m else (None, "")
