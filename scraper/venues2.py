import json, re
from datetime import date, timedelta
from bs4 import BeautifulSoup
from common import *

# ---------- Effenaar (Algolia hits embedded in the page) ----------
def effenaar():
    h = fetch("https://www.effenaar.nl/agenda")
    dec = json.JSONDecoder()
    hits = []
    for m in re.finditer(r'"hits":\[', h):
        try:
            arr, _ = dec.raw_decode(h[m.end() - 1:])
        except Exception:
            continue
        if arr and isinstance(arr[0], dict) and "slug" in arr[0] and len(arr) > len(hits):
            hits = arr
    out = []
    for e in hits:
        st = str(e.get("state") or "")
        if st in ("cancelled",): continue
        try:
            d = datetime.utcfromtimestamp(int(e["date"])).strftime("%Y-%m-%d")
        except Exception:
            continue
        room = ", ".join(l.get("title", "") for l in (e.get("locations") or []))
        out.append(ev("effenaar", d, e["title"], "https://www.effenaar.nl" + e["slug"], "", room,
                      st == "sold_out", bool(e.get("club_card_event"))))
    return out

# ---------- Patronaat ----------
def patronaat():
    s = BeautifulSoup(fetch("https://patronaat.nl/programma/"), "lxml")
    out, seen = [], set()
    for it in s.select(".overview__list-item--event"):
        a = it.select_one('a[href*="/event/"]')
        if not a: continue
        txt = it.get_text("|")
        parts = [clean(x) for x in txt.split("|") if clean(x)]
        d = None
        for p in parts:
            d = parse_nl_date(p)
            if d: break
        # title = the heading-ish element
        t = it.select_one("h2, h3, h4, .event-program__title, [class*=title]")
        title = clean(t.get_text()) if t else (parts[1] if len(parts) > 1 else "")
        if not d or not title: continue
        url = a["href"]
        if url in seen: continue
        seen.add(url)
        tags = [x.lower() for x in parts[2:]]
        low = " ".join(parts).lower()
        if "afgelast" in low or "geannuleerd" in low: continue
        out.append(ev("patronaat", d, title, url, "", "", "uitverkocht" in low or "sold out" in low))
    return out

# ---------- Baroeg (month pages of the Theater plugin) ----------
def baroeg():
    out, seen = [], set()
    today = date.today()
    y, m = today.year, today.month
    for _ in range(16):
        h = fetch(f"https://baroeg.nl/agenda/?wpt_month={y}-{m:02d}")
        s = BeautifulSoup(h, "lxml")
        for e in s.select("div.wp_theatre_event"):
            ds = e.select_one(".wp_theatre_event_startdate")
            a = e.select_one('a[href*="/productie/"]')
            t = e.select_one(".media-heading a, h1 a, h2 a") or a
            title = None
            for sel in ("h1", "h2", ".wp_theatre_prod_title", ".media-body h1 a"):
                x = e.select_one(sel)
                if x and clean(x.get_text()): title = clean(x.get_text()); break
            if not (ds and a and title): continue
            mm = re.search(r"(\d{1,2})/(\d{1,2})/(\d{2})", ds.get_text())
            if not mm: continue
            d = f"20{mm.group(3)}-{int(mm.group(2)):02d}-{int(mm.group(1)):02d}"
            key = (d, title)
            if key in seen: continue
            seen.add(key)
            tm = e.select_one(".wp_theatre_event_starttime")
            low = clean(e.get_text(" ")).lower()
            out.append(ev("baroeg", d, title, a["href"], clean(tm.get_text()) if tm else "", "", "uitverkocht" in low or "sold out" in low))
        m += 1
        if m > 12: y, m = y + 1, 1
    return out

# ---------- Hedon (Angular SSR homepage; year derived from weekday) ----------
WD = {"ma":0,"di":1,"wo":2,"do":3,"vr":4,"za":5,"zo":6}
def infer_date(wd, day, mon):
    today = date.today()
    for yr in (today.year, today.year + 1, today.year + 2):
        try:
            d = date(yr, mon, day)
        except ValueError:
            continue
        if d >= today - timedelta(days=1) and d.weekday() == wd:
            return d.isoformat()
    return None

def hedon():
    s = BeautifulSoup(fetch("https://www.hedon-zwolle.nl/"), "lxml")
    out, seen = [], set()
    for card in s.select("app-event-card"):
        a = card.select_one('a[href^="/voorstelling/"]')
        if not a: continue
        txt = clean(card.get_text(" "))
        m = re.search(r"\b(ma|di|wo|do|vr|za|zo) (\d{1,2}) ([a-z]{3,4})\.?", txt.lower())
        if not m or m.group(3) not in NL_MONTHS: continue
        d = infer_date(WD[m.group(1)], int(m.group(2)), NL_MONTHS[m.group(3)])
        if not d: continue
        title = clean(a.get("title") or "") or None
        if not title:
            rest = re.sub(r"^.*?\d{1,2}:\d{2}\s*", "", txt)
            title = rest
        url = "https://www.hedon-zwolle.nl" + a["href"]
        if url in seen: continue
        seen.add(url)
        low = txt.lower()
        out.append(ev("hedon", d, title, url, "", "", "uitverkocht" in low or "sold out" in low))
    return out
