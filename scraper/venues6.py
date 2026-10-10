"""Zalen 29-39 (oktober 2026): Burgerweeshuis, EKKO, Gebr. de Nobel, Grenswerk, Iduna, Musicon, Q-Factory,
Simplon, Sound Dog, VERA en Victorie. Alles van de eigen sites (of hun eigen ticketwinkel/agenda-bron)."""
import csv, html as _html, io, json, os, re, time
from datetime import date, timedelta
from common import *
import times as _times

UA_PLAIN = {"User-Agent": "BarrysConcertAgenda/1.0 (+https://github.com/bzwijgers/Concerten)"}
EN_MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
WEEKDAYS = {"ma": 0, "mo": 0, "di": 1, "tu": 1, "wo": 2, "we": 2, "do": 3, "th": 3, "vr": 4, "fr": 4, "za": 5, "sa": 5, "zo": 6, "su": 6}
MONTHS = {**NL_MONTHS, **EN_MONTHS, "maa": 3, "mei": 5, "okt": 10, "oct": 10, "may": 5}
DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def _text(h):
    t = re.sub(r"(?s)<(script|style|header|nav|footer).*?</\1>", " ", h)
    return re.sub(r"(\|\s*)+", "| ", re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " | ", t))))


def _infer(wd, day, mon):
    t = date.today()
    for yr in (t.year, t.year + 1, t.year + 2):
        try:
            d = date(yr, mon, day)
        except ValueError:
            continue
        if d >= t - timedelta(days=1) and (wd is None or d.weekday() == wd):
            return d.isoformat()
    return None


def page_date(page):
    """Datum van een concertpagina: schema.org, anders de eerste volledige datum in de tekst, anders weekdag+dag+maand."""
    m = re.search(r'"startDate"\s*:\s*"(\d{4}-\d\d-\d\d)[T ](\d\d):(\d\d)[^"]*?(Z)?"', page)
    if m and m.group(4):   # echte UTC: omrekenen naar Nederlandse tijd (kan de datum verschuiven)
        from datetime import datetime
        from zoneinfo import ZoneInfo
        dt = datetime.fromisoformat(f"{m.group(1)}T{m.group(2)}:{m.group(3)}+00:00").astimezone(ZoneInfo("Europe/Amsterdam"))
        return dt.date().isoformat()
    m = re.search(r'"startDate"\s*:\s*"(\d{4}-\d\d-\d\d)', page)
    if m:
        return m.group(1)
    t = re.sub(r"(\|\s*)+", "| ", re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " | ",
               re.sub(r"(?s)<(script|style|footer).*?</\1>", " ", page)))))[:15000]
    m = re.search(r"\b(ma|di|wo|do|vr|za|zo)\s+(\d{1,2})\.(\d{1,2})\b", t, re.I)    # Simplon: 'za 17.10'
    if m and 1 <= int(m.group(3)) <= 12:
        d = _infer(WEEKDAYS[m.group(1).lower()], int(m.group(2)), int(m.group(3)))
        if d: return d
    m = re.search(r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),?\s+(20\d\d)\b", t, re.I)
    if m:   # OCCII: 'Sunday, October 11, 2026'
        return f"{m.group(3)}-{EN_MONTHS[m.group(1).lower()[:3]]:02d}-{int(m.group(2)):02d}"
    m = re.search(r"\bDatum\s*:?\s*\|?\s*(\d{1,2})-(\d{1,2})(?:-(20\d\d))?\b", t)   # Willem Twee: 'Datum | 14-08'
    if m and 1 <= int(m.group(2)) <= 12:
        if m.group(3): return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
        d = _infer(None, int(m.group(1)), int(m.group(2)))
        if d: return d
    m = re.search(r"\b(\d{1,2})\s+([a-z]{3,10})\.?\s+(20\d\d)\b", t, re.I)
    if m and MONTHS.get(m.group(2).lower()[:3] if m.group(2).lower()[:3] != "maa" else "maa"):
        mon = MONTHS.get(m.group(2).lower()) or MONTHS.get(m.group(2).lower()[:3])
        if mon:
            return f"{int(m.group(3)):04d}-{mon:02d}-{int(m.group(1)):02d}"
    m = re.search(r"\b(ma|di|wo|do|vr|za|zo|mo|tu|we|th|fr|sa|su)[a-z]*[.\s]+(\d{1,2})[.\s]+([a-z]{3,10})\b", t, re.I)
    if m:
        mon = MONTHS.get(m.group(3).lower()) or MONTHS.get(m.group(3).lower()[:3])
        if mon:
            return _infer(WEEKDAYS.get(m.group(1).lower()[:2]), int(m.group(2)), mon)
    m = re.search(r"\b(\d{1,2})\s*\|?\s*(january|february|march|april|may|june|july|august|september|october|november|december|"
                  r"januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)\b", t[:3000], re.I)
    if m:   # Cinetol: '20 | October' (geen jaar, geen weekdag): eerstvolgende
        mon = MONTHS.get(m.group(2).lower()) or MONTHS.get(m.group(2).lower()[:3])
        if mon: return _infer(None, int(m.group(1)), mon)
    return None


def url_date(url):
    """Datum in het adres (De Vorstin: '-17-10-2026/', 'wende-06112026/'): betrouwbaarder dan de paginatekst."""
    m = re.search(r"-(\d{1,2})-(\d{1,2})-(20\d\d)/?$", url) or re.search(r"-(\d{2})(\d{2})(20\d\d)/?$", url)
    if m and 1 <= int(m.group(2)) <= 12 and 1 <= int(m.group(1)) <= 31:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    return None


def page_title(page, strip=""):
    m = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]+)"', page) or re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
    t = clean(re.sub(r"<[^>]+>", " ", m.group(1))) if m else ""
    if strip:
        t = re.sub(r"\s*[-–—|]\s*(" + strip + r").*$", "", t, flags=re.I)
    return t.strip()


class Details:
    """Detailpagina's met geheugen (data/details.json): voorbije concerten nooit opnieuw, toekomstige wekelijks."""
    def __init__(self):
        self.path = os.path.join(DATA, "details.json")
        try:
            self.c = json.load(open(self.path, encoding="utf-8"))
        except Exception:
            self.c = {}

    def get(self, url, strip="", budget=None):
        today = date.today().isoformat()
        x = self.c.get(url)
        fresh = x and x.get("v") == 2 and (x.get("d") and x["d"] < today or x.get("at", "") >= (date.today() - timedelta(days=7)).isoformat())
        if fresh or (budget is not None and budget[0] <= 0):
            return x
        if budget is not None: budget[0] -= 1
        try:
            p = fetch(url, tries=2, timeout=30)
            title = page_title(p, strip)
            t = _text(p)
            i = t.find(title[:30]) if title else -1    # 'uitverkocht' alleen als het bij de titel staat
            sold = i >= 0 and bool(re.search(r"\buitverkocht\b|\bsold\s*out\b", t[max(0, i - 120):i + 250], re.I))
            x = {"d": url_date(url) or page_date(p), "n": title, "t": _times.find_time(p), "at": today, "s": sold, "v": 2}
            zm = (re.search(r"\bZaal\s*:?\s*\|\s*([^|:]{2,40})\|", t)
                  or re.search(r"\b(?:Locatie|Location)\s*:?\s*\|\s*([^|:]{2,40})\|", t))
            if zm: x["r"] = zm.group(1).strip()
        except Exception as ex:
            print("detail mislukt:", url, ex)
            x = x or {"d": None, "n": "", "t": "", "at": today}
        self.c[url] = x
        time.sleep(0.7)
        return x

    def save(self):
        json.dump(self.c, open(self.path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))


DET = Details()


def _from_urls(key, urls, strip, limit=150):
    budget, out = [limit], []
    for u in urls:
        x = DET.get(u, strip, budget)
        if x and x.get("d") and x.get("n"):
            out.append(ev(key, x["d"], x["n"], u, x.get("t", ""), x.get("r", ""), x.get("s", False)))
    DET.save()
    return out


def _links(page, base, pattern):
    seen, out = set(), []
    for href in re.findall(r'href="([^"#?]+)[^"]*"', page):
        u = href if href.startswith("http") else base + href
        u = u.rstrip("/") + "/" if u.endswith("/") else u
        if re.search(pattern, u) and u not in seen:
            seen.add(u); out.append(u)
    return out


# ---------- The Events Calendar (WordPress) ----------
def tribe(key, base):
    out, url, n = [], f"{base}/wp-json/tribe/events/v1/events/?per_page=50&start_date={date.today().isoformat()}", 0
    while url and n < 10:
        j = json.loads(fetch(url, headers=UA_PLAIN))
        for x in j.get("events", []):
            title = clean(x.get("title"))
            sold = bool(re.search(r"sold\s*out|uitverkocht", title, re.I))
            title = re.sub(r"^\s*\*?\s*(sold\s*out|uitverkocht)\s*\*?\s*[:\-–]?\s*", "", title, flags=re.I).strip()
            d, t = split_dt(x.get("start_date"))
            if d and title and x.get("status") in (None, "publish"):
                out.append(ev(key, d, title, (x.get("url") or "").split("?")[0], t, "", sold))
        url, n = j.get("next_rest_url"), n + 1
        time.sleep(1)
    return out


def musicon():
    return tribe("musicon", "https://musicon.nl")


# ---------- EKKO: WordPress-API met datum/tijd in acf ----------
def ekko():
    out, page = [], 1
    while page <= 10:
        try:
            j = json.loads(fetch(f"https://ekko.nl/wp-json/wp/v2/event?per_page=100&page={page}", headers=UA_PLAIN))
        except RuntimeError:
            break
        if not j: break
        for x in j:
            a = x.get("acf") or {}
            d, t = split_dt(a.get("date_time") or "")
            title = clean(x["title"]["rendered"])
            if "/en/" in x.get("link", "") or x.get("lang") == "en": continue   # Engelse versie van dezelfde pagina
            if d:
                out.append(ev("ekko", d, title, x["link"], t, "", False))
        if len(j) < 100: break
        page += 1
        time.sleep(1)
    return out


# ---------- Stager (ticketwinkel van de zaal zelf; toont de eerstvolgende 50) ----------
def stager(key, shop, place_filter=None):
    out = []
    for o in ld_events(fetch(f"https://{shop}/shop/default", headers=UA_PLAIN)):
        if cancelled(o): continue
        d, t = split_dt(o.get("startDate"))
        loc = ((o.get("location") or {}).get("address") or {}).get("addressLocality", "")
        if not d or (place_filter and loc and place_filter.lower() not in loc.lower()): continue
        room = (o.get("location") or {}).get("name", "")
        out.append(ev(key, d, o.get("name", ""), o.get("url") or "", t, room, sold_from_offers(o)))
    return out


def vera():
    return stager("vera", "vera.stager.co", "Groningen")


def grenswerk():
    return [e for e in stager("grenswerk", "grenswerk.stager.co", "Venlo") if not re.search(r"^club grenswerk \d{4}$", e["n"], re.I)]


# ---------- lijstpagina + detailpagina's ----------
def simplon():
    urls = _links(fetch("https://simplon.nl/programma/"), "https://simplon.nl", r"simplon\.nl/events/[^/]+/$")
    got = {e["u"]: e for e in stager("simplon", "simplon.stager.co", "Groningen")}
    return _from_urls("simplon", urls, "Simplon") or list(got.values())


def burgerweeshuis():
    urls = _links(fetch("https://www.burgerweeshuis.nl/programma"), "https://www.burgerweeshuis.nl", r"burgerweeshuis\.nl/events/[^/]+$")
    return _from_urls("burgerweeshuis", urls, "Burgerweeshuis")


def victorie():
    urls = _links(fetch("https://www.podiumvictorie.nl/programma/"), "https://www.podiumvictorie.nl", r"podiumvictorie\.nl/programma/[^/]+/$")
    return _from_urls("victorie", urls, "Podium Victorie|Victorie")


def iduna():
    urls, page = [], 1
    while page <= 6:
        try:
            j = json.loads(fetch(f"https://iduna.nl/wp-json/wp/v2/agenda?per_page=100&page={page}&orderby=date&order=desc", headers=UA_PLAIN))
        except RuntimeError:
            break
        urls += [x["link"] for x in j]
        if len(j) < 100: break
        page += 1
    return _from_urls("iduna", urls, "Iduna", limit=200)


def qfactory():
    sm = fetch("https://q-factory.com/sitemap.xml", headers=UA_PLAIN)
    urls = [u for u in re.findall(r"<loc>([^<]+)</loc>", sm) if "/en/events/" in u]
    return [e for e in _from_urls("qfactory", urls, "Q-Factory") if e["d"]]


# ---------- Gebr. de Nobel: datum staat in het adres ----------
def nobel():
    h = fetch("https://nobel.nl/agenda")
    out, seen = [], set()
    for href, inner in re.findall(r'href="(/agenda/[a-z0-9-]+-(?:\d{1,2})-[a-z]{3}-\d{4})"[^>]*>(.*?)</a>', h, re.S):
        if href in seen: continue
        m = re.search(r"-(\d{1,2})-([a-z]{3})-(\d{4})$", href)
        mon = EN_MONTHS.get(m.group(2)) or NL_MONTHS.get(m.group(2))
        if not mon: continue
        seen.add(href)
        h3 = re.search(r"<h3[^>]*>(.*?)</h3>", inner, re.S)
        title = clean(re.sub(r"<[^>]+>", " ", h3.group(1) if h3 else inner))
        slugtitle = href.split("/")[-1][:m.start() - len(href.split("/")[-1])].replace("-", " ").strip()
        title = re.sub(r"\s+\d{1,2}\s+[A-Za-z]{3}\.?$", "", title).strip()     # 'Audrey Horne 13 Oct'
        if not title or len(title) > 120:
            title = slugtitle.title()
        out.append(ev("nobel", f"{m.group(3)}-{mon:02d}-{int(m.group(1)):02d}", title, "https://nobel.nl" + href, "", "",
                      "uitverkocht" in inner.lower()))
    return out


# ---------- Sound Dog: de agenda op hun site komt uit hun eigen gepubliceerde spreadsheet ----------
SOUNDDOG_CSV = ("https://docs.google.com/spreadsheets/d/e/2PACX-1vQZFG55vV25jl46jsdFp5cHpCmU4pyWzZ0SX2ytKT9TKT9F5k3s_y08GWUfk5G3"
                "YlbSm0WI5abigD0G/pub?output=csv")


def sounddog():
    rows = list(csv.reader(io.StringIO(fetch(SOUNDDOG_CSV, headers=UA_PLAIN))))
    out, seen = [], set()
    for r in rows:
        if len(r) < 17 or not re.match(r"\d{4}-\d\d-\d\d$", r[0]): continue
        kind = (r[16] or "").strip().lower()
        if kind not in ("concert", "concerten", "show", "live"): continue
        k = (r[0], r[3].strip())
        if k in seen or not r[3].strip(): continue
        seen.add(k)
        t = r[6].strip() if re.match(r"\d{1,2}:\d\d$", r[6].strip()) else ""
        slug = re.sub(r"[^a-z0-9]+", "-", r[3].lower()).strip("-")[:40]
        out.append(ev("sounddog", r[0], r[3], f"https://sounddogbreda.nl/#{r[0]}-{slug}", t, "", False))
    return out
