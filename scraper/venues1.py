import json, re
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from common import *

# ---------- Rotown (JSON-LD on the homepage; Clubcard = ticket link in /shop/clubcard/) ----------
def rotown():
    out = []
    for o in ld_events(fetch("https://www.rotown.nl/")):
        d, t = split_dt(o.get("startDate"))
        if not d or cancelled(o): continue
        offers = o.get("offers") or {}
        ou = offers.get("url", "") if isinstance(offers, dict) else ""
        loc = (o.get("location") or {}).get("name", "")
        out.append(ev("rotown", d, o["name"], o["url"], t, "" if loc.lower() == "rotown" else loc,
                      sold_from_offers(o), "/shop/clubcard/" in ou))
    return out

# ---------- Paard ----------
def paard():
    out = []
    for o in ld_events(fetch("https://www.paard.nl/event/")):
        d, t = split_dt(o.get("startDate"))
        if not d or cancelled(o) or not o.get("url"): continue
        out.append(ev("paard", d, o["name"], o["url"], t, (o.get("location") or {}).get("name", ""), sold_from_offers(o)))
    return out

# ---------- De Helling ----------
def helling():
    out = []
    for o in ld_events(fetch("https://dehelling.nl/agenda/")):
        d, t = split_dt(o.get("startDate"))
        if not d or cancelled(o) or not o.get("url"): continue
        out.append(ev("helling", d, o["name"], o["url"], t, "", sold_from_offers(o)))
    return out

# ---------- Mezz (WordPress REST) ----------
def mezz():
    out, page = [], 1
    while True:
        try:
            data = fetch_json(f"https://www.mezz.nl/wp-json/wp/v2/event?per_page=100&page={page}")
        except RuntimeError:
            break
        if not data: break
        for e in data:
            ev_ = e.get("event") or {}
            prod = e.get("prod") or {}
            d = parse_nl_date(ev_.get("start", ""))
            if not d or not prod.get("title"): continue
            status = str(ev_.get("status", "")).lower()
            if "cancel" in status or "afgelast" in status: continue
            cl = " ".join(e.get("class_list") or [])
            if "category-concert" not in cl and "category-" in cl and "category-festival" not in cl:
                # keep everything that is not obviously a night/club event
                if "category-bynight" in cl or "category-club" in cl: continue
            out.append(ev("mezz", d, prod["title"], prod.get("link") or e.get("link"), "", "", "sold" in status or "uitverkocht" in status))
        if len(data) < 100: break
        page += 1
    return out

# ---------- De Boerderij (ajax feed; titles come from the event pages) ----------
def boerderij():
    data = fetch_json("https://poppodiumboerderij.nl/includes/ajax/events.php?limit=200&offset=0")
    items = [e for e in data if e.get("event_date") and e.get("seo_slug")]
    def title(e):
        url = f"https://poppodiumboerderij.nl/programma/{e['seo_slug']}/"
        t = e.get("title") or ""
        if not t:
            try:
                h = fetch(url)
                m = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S) or re.search(r"<title>(.*?)</title>", h, re.S)
                t = re.sub(r"<[^>]+>", "", m.group(1)) if m else e["seo_slug"]
                t = re.sub(r"\s*[|\-–]\s*(Poppodium )?(De )?Boerderij.*$", "", clean(t))
            except Exception:
                t = e["seo_slug"]
        return ev("boerderij", e["event_date"], t, url, "", e.get("stage", ""), False)
    with ThreadPoolExecutor(6) as ex:
        return list(ex.map(title, items))

# ---------- Melkweg (homepage list reaches ~1 year) ----------
def melkweg():
    h = fetch("https://www.melkweg.nl/nl/agenda/")
    s = BeautifulSoup(h, "lxml")
    out = []
    for day in s.select('[class*="event-list-day__title"] time'):
        d = day.get("datetime") or day.get("dateTime")
        ol = day.find_parent().find_next_sibling("ol")
        if not d or not ol: continue
        for a in ol.select('a[href*="/nl/agenda/"]'):
            t = a.select_one("h3")
            if not t: continue
            txt = clean(a.get_text(" "))
            out.append(ev("melkweg", d, t.get_text(), "https://www.melkweg.nl" + a["href"], "", "", "uitverkocht" in txt.lower()))
    return out

# ---------- 013 ----------
def o13():
    h = fetch("https://www.013.nl/programma")
    if "<article" not in h:   # 2026-10-10 een keer een pagina zonder programma gekregen: nog een poging, anders bewaren
        time.sleep(30)
        h = fetch("https://www.013.nl/programma")
        if "<article" not in h:
            p = os.path.join(os.path.dirname(__file__), "..", "data", "samples")
            os.makedirs(p, exist_ok=True)
            open(os.path.join(p, "o13_leeg.html"), "w", encoding="utf-8").write(h)
    s = BeautifulSoup(h, "lxml")
    out = []
    for art in s.select("article"):
        a = art.select_one('a[href*="/programma/"]'); t = art.select_one("h2"); tm = art.select_one("time")
        if not (a and t and tm and tm.get("datetime")): continue
        d, hm = split_dt(tm["datetime"])
        txt = clean(art.get_text(" ")).lower()
        out.append(ev("o13", d, t.get_text(), a["href"], hm, "", "uitverkocht" in txt))
    return out

# ---------- Dynamo ----------
def dynamo():
    s = BeautifulSoup(fetch("https://www.dynamo-eindhoven.nl/evenementen/"), "lxml")
    out, seen = [], set()
    for a in s.select('a[href*="/evenement/"]'):
        h3 = a.select_one("h3")
        if not h3: continue
        d = parse_nl_date(a.get_text(" ")[:60])
        url = a["href"]
        if not d or url in seen: continue
        seen.add(url)
        parts = [clean(x) for x in a.select_one("div").get_text("|").split("|") if clean(x)]
        room = parts[1] if len(parts) > 2 else ""
        out.append(ev("dynamo", d, h3.get_text(), url, "", room, "uitverkocht" in clean(a.get_text(" ")).lower()))
    return out

# ---------- Paradiso (sitemap + event pages, cached by lastmod) ----------
def paradiso(cache):
    idx = fetch("https://www.paradiso.nl/sitemap.xml")
    maps = re.findall(r"<loc>(https://www\.paradiso\.nl/sitemap/event_\d+\.xml)</loc>", idx)
    entries = {}
    def read(u):
        x = fetch(u)
        for m in re.finditer(r"<loc>(https://www\.paradiso\.nl/programma/([^/<]+)/(\d+))</loc>\s*<lastmod>([^<]+)</lastmod>", x):
            entries[m.group(3)] = (m.group(1), m.group(4))
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(read, maps))
    today = date.today().isoformat()
    todo = []
    for id_, (url, lm) in entries.items():
        if int(id_) < 2300000: continue
        c = cache.get(id_)
        if c and c.get("lm") == lm and (c.get("d") is None or c["d"] < today):
            continue          # past or unchanged-and-known
        if c and c.get("lm") == lm:
            continue
        if lm[:4] < "2026" and not c and int(id_) < 2700000: continue
        todo.append((id_, url, lm))
    def get(t):
        id_, url, lm = t
        try:
            h = fetch(url)
        except Exception:
            return None
        evs = ld_events(h)
        if not evs: return id_, {"lm": lm, "d": None}
        o = evs[0]
        d, tm = split_dt(o.get("startDate"))
        st = str(o.get("eventStatus", ""))
        loc = (o.get("location") or {}).get("name", "")
        txt = re.sub(r"<[^>]+>", " ", h).lower()
        sold = "uitverkocht" in txt[:60000] and "sold out" in txt[:60000] or "ticketstatus--soldout" in h.lower()
        rec = {"lm": lm, "d": d, "t": tm, "n": o.get("name"), "u": url, "r": loc, "s": sold,
               "x": ("Cancel" in st or "Postponed" in st or "Rescheduled" in st)}
        return id_, rec
    with ThreadPoolExecutor(8) as ex:
        for res in ex.map(get, todo):
            if res: cache[res[0]] = res[1]
    out = []
    for id_, c in cache.items():
        if c.get("d") and not c.get("x") and c.get("n"):
            out.append(ev("paradiso", c["d"], c["n"], c["u"], c.get("t", ""), c.get("r", ""), c.get("s", False)))
    return out
