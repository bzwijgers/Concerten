"""Aanvangstijden aanvullen voor zalen waarvan de lijstpagina geen tijd geeft.
Per concert wordt de eigen detailpagina hooguit één keer gelezen; de gevonden tijd wordt onthouden in data/times.json."""
import html as _html, json, os, re, time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from common import fetch

VENUES = ("melkweg", "effenaar", "hedon", "mezz", "patronaat", "pul", "dynamo", "boerderij", "gebouwt", "amare")
PER_VENUE = 120     # nieuwe pagina's per zaal per run
RETRY_DAYS = 14     # niets gevonden: na zoveel dagen opnieuw proberen (tijd kan later bekend worden)

START = r"aanvang|start|begin|showtime|show"
DOOR = r"zaal\s*open|deuren(?:\s*open)?|doors(?:\s*open)?|open"


def _text(h):
    t = re.sub(r"(?s)<(script|style).*?</\1>", " ", h)
    t = _html.unescape(re.sub(r"<[^>]+>", " | ", t))
    return re.sub(r"(\|\s*)+", "| ", re.sub(r"\s+", " ", t))


def _hm(h, m):
    h = int(h)
    return f"{h:02d}:{m}" if 0 <= h <= 23 else None


def find_time(page):
    """'20:30' voor een aanvangstijd, 'deuren 19:30' als alleen de deurtijd betrouwbaar is, anders ''."""
    for sd in re.findall(r'"startDate"\s*:\s*"(\d{4}-\d\d-\d\d)[T ](\d\d):(\d\d)', page)[:1]:
        if sd[1:] != ("00", "00"):
            return f"{sd[1]}:{sd[2]}"          # zoals de zaal het schrijft (geen tijdzone-omrekening)
    m = re.search(r'class="[^"]*date__time[^"]*">\s*(\d{1,2}):(\d{2})\s*<', page)   # Melkweg: tijd in de paginakop
    if m and _hm(m.group(1), m.group(2)):
        return _hm(m.group(1), m.group(2))
    t = _text(page)[:12000]
    lab = r"(?i)\b(" + START + "|" + DOOR + r")\b\s*:?\s*\|?\s*(?:om\s*)?(\d{1,2})[:.](\d{2})"
    start = door = None
    for m in re.finditer(lab, t):
        v = _hm(m.group(2), m.group(3))
        if not v: continue
        if re.fullmatch(START, m.group(1), re.I):
            start = start or v
        else:
            door = door or v
        if start and door: break
    if start and (not door or start >= door):
        return start
    if door:
        return "deuren " + door
    return ""


def fill(events_by_venue, data_dir):
    """events_by_venue: {venue: [event,...]} (de verse lijsten). Vult e['t'] waar die leeg is."""
    path = os.path.join(data_dir, "times.json")
    try:
        cache = json.load(open(path, encoding="utf-8"))
    except Exception:
        cache = {}
    today = date.today().isoformat()
    retry = (date.today() - timedelta(days=RETRY_DAYS)).isoformat()

    def work(v):
        n = 0
        for e in events_by_venue.get(v, []):
            if e.get("t"): continue
            c = cache.get(e["u"])
            if c and (c["t"] or c["at"] >= retry):
                e["t"] = c["t"]; continue
            if n >= PER_VENUE: continue
            n += 1
            try:
                e["t"] = find_time(fetch(e["u"], tries=2, timeout=30))
            except Exception:
                e["t"] = ""
            cache[e["u"]] = {"t": e["t"], "at": today}
            time.sleep(1)
        return v, n

    with ThreadPoolExecutor(6) as ex:
        for v, n in ex.map(work, [v for v in VENUES if v in events_by_venue]):
            if n: print(f"tijden {v}: {n} pagina's gelezen")
    live = {e["u"] for g in events_by_venue.values() for e in g}
    cache = {u: c for u, c in cache.items() if u in live or c["at"] >= retry}
    json.dump(cache, open(path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
