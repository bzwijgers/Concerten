"""Tolhuistuin (eigen programma) en Amare (Den Haag)."""
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
            if "klassieke muziek" in genres or BAD_TITLE.search(title): continue
            if not (set(genres) & GOOD): continue
            d = _infer(WD.get(st.group(1)), int(st.group(2)), NL_MONTHS.get(st.group(3)))
            if not d: continue
            tm = re.search(r'class="time">\s*/\s*(\d{1,2}:\d{2})', b)
            v = re.search(r'class="venue">\s*(.*?)\s*</div>', b, re.S)
            href = u.group(1)
            out.append(ev("amare", d, title, "https://www.amare.nl" + href if href.startswith("/") else href,
                          tm.group(1) if tm else "", clean(v.group(1)) if v else ""))
        if not new or n >= max_pages: break
        n += 1
        time.sleep(delay)
        page = _get(f"https://www.amare.nl/nl/agenda?{pname}_page={n}")
    print(f"amare: {n} pagina's, {len(seen)} items, {len(out)} concerten")
    return out
