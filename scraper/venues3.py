import json, re
from datetime import date, timedelta
from bs4 import BeautifulSoup
from common import *

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

NON_MUSIC = {"cabaret", "theater", "comedy"}

# ---------- Hedon (JSON API behind the Angular site) ----------
def hedon():
    data = fetch_json("https://www.hedon-zwolle.nl/api/events")
    out = []
    for e in data:
        if not e.get("publish", True): continue
        genres = {g.get("name", "").lower() for g in e.get("genres") or []}
        if genres and genres <= NON_MUSIC: continue
        d, tm = split_dt((e.get("eventDate") or "").replace("Z", ""))
        if not d: continue
        title = e.get("title") or ""
        if not title: continue
        st = e.get("status")
        venue = e.get("venue") or ""
        room = venue.replace("Hedon - ", "") if venue.startswith("Hedon") else venue
        url = f"https://www.hedon-zwolle.nl/voorstelling/{e['id']}/" + slug_(title)
        out.append(ev("hedon", d, title, url, "", room, st in (2, 5)))
    return out

def slug_(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

# ---------- De Pul (query.php returns HTML snippets; date without year -> infer from weekday) ----------
def pul():
    out, shown, seen = [], 0, set()
    for _ in range(40):
        j = fetch_json(f"https://www.livepul.com/query.php?source=agenda&agenda_page=true&month=all&search=false&amount_of_events_already_shown={shown}")
        s = BeautifulSoup(j.get("output", ""), "lxml")
        cards = s.select("a.agenda-event--actual-event")
        if not cards: break
        for a in cards:
            ds = a.select_one(".agenda-event__date"); t = a.select_one(".agenda-event__title")
            if not (ds and t): continue
            m = re.match(r"\s*(ma|di|wo|do|vr|za|zo)\s+(\d{1,2})\s+([a-z]{3,4})", clean(ds.get_text()).lower())
            if not m or m.group(3) not in NL_MONTHS: continue
            d = infer_date(WD[m.group(1)], int(m.group(2)), NL_MONTHS[m.group(3)])
            if not d: continue
            url = "https://www.livepul.com" + a["href"]
            if url in seen: continue
            seen.add(url)
            low = clean(a.get_text(" ")).lower()
            out.append(ev("pul", d, t.get_text(), url, "", "", "uitverkocht" in low or "sold out" in low))
        shown += len(cards)
        if not j.get("show_more_possible"): break
    return out
