"""Tolhuistuin (eigen programma), Amare (Den Haag) en Het Bolwerk (Sneek)."""
import html as _html, json, re, time, urllib.request, http.cookiejar
from datetime import date, timedelta
from common import *

# ---------- Tolhuistuin: de agenda-pagina bevat alle items als JSON, met een vlag voor 'staat ook bij Paradiso' ----------
def tolhuistuin():
    h = fetch("https://tolhuistuin.nl/agenda/")
    m = re.search(r":all-items='(.*?)'\s", h, re.S)
    if not m:
        raise RuntimeError("tolhuistuin: geen items gevonden")
    items = json.loads(_html.unescape(m.group(1)))
    out = []
    for e in items:
        if e.get("paradisoEvent"): continue
        if (e.get("eventType") or {}).get("label") not in ("Muziek", "Festival"): continue
        d, _, t = (e.get("eventStartDate") or "").partition(" ")
        d = d.replace("/", "-")
        if not re.match(r"\d{4}-\d\d-\d\d$", d): continue
        out.append(ev("tolhuistuin", d, e["title"], e["url"], t[:5], e.get("location") or "", e.get("soldOut")))
    return out

# ---------- Amare (CultureSuite): lijstpagina's met genres; robots.txt: crawl-delay 5 s, ?p<N>_page= toegestaan ----------
WD = {"ma": 0, "di": 1, "wo": 2, "do": 3, "vr": 4, "za": 5, "zo": 6}
GOOD = {"pop", "rock", "global", "singer-songwriter", "indie", "folk", "blues", "soul", "hiphop", "brasil & luso", "wereldmuziek", "country", "reggae", "metal", "punk"}
BAD_TITLE = re.compile(r"workshop|social dance|rondleiding|open mic|familiezondag|expositie|lezing|college", re.I)

def _infer(wd, day, mon):
    t = date.today()
    for yr in (t.year, t.year + 1, t.year + 2):
        try:
            d = date(yr, mon, day)
        except ValueError:
            continue
        if d >= t - timedelta(days=1) and d.weekday() == wd:
            return d.isoformat()
    return None

_opener = None
def _get(url):
    global _opener
    if FIXTURES:
        return fetch(url)
    if _opener is None:
        _opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        _opener.addheaders = [("User-Agent", UA), ("Accept-Language", "nl,en;q=0.8")]
    for i in range(3):
        try:
            with _opener.open(url, timeout=40) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as ex:
            last = ex; time.sleep(5 * (i + 1))
    raise RuntimeError(f"amare: {url}: {last}")

def amare(max_pages=70, delay=5.0):
    out, seen = [], set()
    global _opener
    first = _get("https://www.amare.nl/nl/agenda")
    for wait in (60, 180):   # Amare heeft bij drukte een wachtrij (/csq/): later gewoon opnieuw
        if "data-entry-id=" in first or FIXTURES: break
        print(f"amare: geen programma (wachtrij?), over {wait} s opnieuw")
        time.sleep(wait); _opener = None
        first = _get("https://www.amare.nl/nl/agenda")
    pm = re.search(r"\?(p\d+)_page=\d+", first)
    pname = pm.group(1) if pm else "p54"
    page, n = first, 1
    while True:
        cards = list(re.finditer(r'<li\s+data-entry-id="(\d+)"(.*?)(?=<li\s+data-entry-id=|</ul>\s*</div>\s*<)', page, re.S))
        if not cards: break
        new = 0
        for c in cards:
            b = c.group(2)
            if c.group(1) in seen: continue
            seen.add(c.group(1)); new += 1
            u = re.search(r'class="desc"\s+href="([^"]+)"', b)
            t = re.search(r'class="title">(.*?)</h3>', b, re.S)
            st = re.search(r'class="start">\s*([a-z]{2})\s+(\d{1,2})\s+([a-z]{3})', b)
            if not (u and t and st): continue
            genres = [x.strip().lower() for x in re.findall(r'genres__link"[^>]*>([^<]*)<', b)]
            title = clean(re.sub(r"<[^>]+>", " ", t.group(1)))
            sold = bool(re.search(r"\*?\s*uitverkocht\s*\*?", title, re.I))
            title = re.sub(r"\*?\s*uitverkocht\s*\*?|[-–]?\s*laatste kaarten\s*[-–]?", " ", title, flags=re.I)
            title = re.sub(r"\s+", " ", title).strip(" -–")
            if "klassieke muziek" in genres or BAD_TITLE.search(title): continue
            if not (set(genres) & GOOD): continue
            d = _infer(WD.get(st.group(1)), int(st.group(2)), NL_MONTHS.get(st.group(3)))
            if not d: continue
            tm = re.search(r'class="time">\s*/\s*(\d{1,2}:\d{2})', b)
            v = re.search(r'class="venue">\s*(.*?)\s*</div>', b, re.S)
            href = u.group(1)
            out.append(ev("amare", d, title, "https://www.amare.nl" + href if href.startswith("/") else href,
                          tm.group(1) if tm else "", clean(v.group(1)) if v else "", sold))
        if not new or n >= max_pages: break
        n += 1
        time.sleep(delay)
        page = _get(f"https://www.amare.nl/nl/agenda?{pname}_page={n}")
    print(f"amare: {n} pagina's, {len(seen)} items, {len(out)} concerten")
    return out

# ---------- Het Bolwerk (Sneek), onderdeel van Poort: ontdekpoort.nl ----------
# Elke pagina bevat de zoekindex van het hele programma (JSON). Daaruit de muziek in het Bolwerk;
# per concert levert de eigen detailpagina datum mét jaartal, aanvang en status.
# De site weigert user-agents die zich als 'Mozilla/5.0 (compatible; ...)' voordoen; daarom hier de
# naam van de agenda zonder dat voorvoegsel. robots.txt staat alles toe.
POORT_UA = "BarrysConcertAgenda/1.0 (+https://github.com/bzwijgers/Concerten)"
_DOW = {"ma": 0, "di": 1, "wo": 2, "do": 3, "vr": 4, "za": 5, "zo": 6}

def bolwerk(delay=1.0):
    hdr = {"User-Agent": POORT_UA}
    h = fetch("https://ontdekpoort.nl/programma/locatie/bolwerk-kerkgracht-8/", headers=hdr)
    m = re.search(r'id="Navbar_Search_Events">(.*?)</script>', h, re.S)
    if not m:
        import os
        p = os.path.join(os.path.dirname(__file__), "..", "data", "samples")
        os.makedirs(p, exist_ok=True)
        open(os.path.join(p, "bolwerk_leeg.html"), "w", encoding="utf-8").write(h[:200000])   # om te zien wat Poort teruggaf
        raise RuntimeError("bolwerk: geen zoekindex gevonden")
    items = [x for x in json.loads(m.group(1)) if (x.get("meta") or "").startswith("Bolwerk")]
    out = []
    import os
    cpath = os.path.join(os.path.dirname(__file__), "..", "data", "bolwerk_cache.json")
    try:
        cache = json.load(open(cpath, encoding="utf-8"))
    except Exception:
        cache = {}
    week_ago = (date.today() - timedelta(days=7)).isoformat()
    for x in items:
        st = (x.get("search_text") or "").lower()
        tail = st.rsplit("bolwerk - kerkgracht 8", 1)[-1].split()
        if "muziek" not in tail: continue          # categorie staat achteraan, bv. 'muziek rock', 'heavy muziek'
        title, url = clean(x["title"]), x["url"]
        c = cache.get(url)
        if c and c.get("at", "") >= week_ago and c.get("shows"):   # pagina deze week al gelezen
            shows = [tuple(s) for s in c["shows"]]
        else:
            shows = []
            try:
                time.sleep(delay)
                dh = fetch(url, headers=hdr)
                for li in re.findall(r'<li\b[^>]*>(.*?)</li>', (re.search(r'event-shows-list(.*?)</ul>', dh, re.S) or [None, ""])[1], re.S):
                    d = parse_nl_date(re.sub(r"<[^>]+>", " ", li))
                    if not d: continue
                    tm = re.search(r"Aanvang:?\s*(?:om\s*)?(\d{1,2}[:.]\d{2})", li)
                    sold = bool(re.search(r"uitverkocht|sold\s*out", li, re.I))
                    shows.append((d, tm.group(1).replace(".", ":") if tm else "", sold))
                if shows: cache[url] = {"at": date.today().isoformat(), "shows": shows}
            except Exception as ex:
                print("bolwerk: detail mislukt", url, ex)
                if c and c.get("shows"): shows = [tuple(s) for s in c["shows"]]
        if not shows:   # terugval: datum uit de index, jaar via de weekdag
            dm = re.match(r"([a-z]{2})\s+(\d{1,2})\s+([a-z]+)", (x.get("lines") or [""])[0].lower())
            d = dm and NL_MONTHS.get(dm.group(3)) and _infer(_DOW.get(dm.group(1)), int(dm.group(2)), NL_MONTHS[dm.group(3)])
            if d: shows.append((d, "", False))
        for d, t, sold in shows:
            out.append(ev("bolwerk", d, title, url, t, "", sold))
    live = {x["url"] for x in items}
    json.dump({u: c for u, c in cache.items() if u in live}, open(cpath, "w", encoding="utf-8"), separators=(",", ":"))
    print(f"bolwerk: {len(items)} items in het Bolwerk, {len(out)} concerten")
    return out

# ---------- dB's (Utrecht): de agenda-API van hun eigen WordPress-site (The Events Calendar) ----------
def dbs():
    out, url, n = [], f"https://dbstudio.nl/wp-json/tribe/events/v1/events/?per_page=50&start_date={date.today().isoformat()}", 0
    while url and n < 10:
        j = json.loads(fetch(url, headers={"User-Agent": POORT_UA}))
        for x in j.get("events", []):
            v = x.get("venue") or {}
            if isinstance(v, dict) and v.get("city") and v["city"].lower() != "utrecht": continue
            if x.get("status") not in (None, "publish"): continue
            title = clean(x.get("title"))
            sold = bool(re.search(r"sold\s*out|uitverkocht", title, re.I))
            title = re.sub(r"^\s*\*?\s*(sold\s*out|uitverkocht)\s*\*?\s*[:\-–]?\s*", "", title, flags=re.I).strip()
            if BAD_TITLE.search(title): continue
            d, t = split_dt(x.get("start_date"))
            if d and title:
                out.append(ev("dbs", d, title, (x.get("url") or "").split("?")[0], t, "", sold))
        url, n = j.get("next_rest_url"), n + 1
        time.sleep(1)
    return out
