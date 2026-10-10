"""Ticketmaster Discovery API (officiële API, eigen sleutel van de eigenaar in GitHub-secret TM_API_KEY).
Alle muziekevenementen in Nederland; locaties die we al zelf van de zaalsite halen worden overgeslagen,
en wat op dezelfde dag met een gelijkende titel al in de agenda staat ook."""
import json, os, re, time, urllib.parse, urllib.request, urllib.error
from datetime import date, datetime, timedelta

API = "https://app.ticketmaster.com/discovery/v2/events.json"
MUSIC = "KZFzniwnSyZfZ7v7nJ"   # segment Music

# locaties die we al zelf uitlezen (genormaliseerde naam, deel van de Ticketmaster-locatienaam)
OWN = ["paradiso", "melkweg", "013", "tivolivredenburg", "tivoli", "effenaar", "doornroosje", "paard", "mezz",
       "depul", "boerderij", "patronaat", "hedon", "dehelling", "dynamo", "klokgebouw", "metropool", "spotgroningen",
       "oosterpoort", "bibelot", "bosuil", "birdrotterdam", "gebouwt", "neushoorn", "amare", "tolhuistuin", "rotown",
       "baroeg", "dbs", "bolwerk", "ontdekpoort", "burgerweeshuis", "ekko", "nobel", "grenswerk", "iduna", "musicon",
       "qfactory", "simplon", "sounddog", "vera", "victorie",
       "luxorlive", "willemtwee", "gigant", "fluor", "vorstin", "p3purmerend", "demeester", "occii", "cinetol", "groeneengel", "backstagebridges", "muziekgieterij", "poppodiumvolt", "dekade", "nieuwenor", "annabel", "halloffame", "hallfame"]
# horeca/arrangementen bij grote zalen: geen aparte zaal
HOSPITALITY = re.compile(r"\b(loge|lounge|skybox|hospitality)\b|ziggo\s*dome\s*club", re.I)
# geen klassiek, jazz of dance (zelfde regel als bij Tivoli)
SKIP_GENRES = re.compile(r"\bclassical\b|\bklassiek\b|\bjazz\b|\bdance\b|electronic|elektronisch|\bopera\b|\bkinder|\bchildren", re.I)
JUNK = re.compile(r"\b(parkeren|parkeer\w*|parking|upgrade|vip[\s-]*(package|pakket|ticket|upgrade|experience)|hospitality|"
                  r"locker|kluisje|camping|shuttle|busreis|bustickets?|garderobe|cadeaukaart|gift\s*card|voucher|"
                  r"meet\s*(&|and|en)\s*greet|skybox|arrangement|fan\s*pakket|early\s*entry|packages?)\b", re.I)


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:40]


class TMError(RuntimeError):
    pass


def _get(params, key):
    q = urllib.parse.urlencode({**params, "apikey": key})
    for i in range(4):
        try:
            req = urllib.request.Request(API + "?" + q, headers={"User-Agent": "BarrysConcertAgenda/1.0 (+https://github.com/bzwijgers/Concerten)"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise TMError(f"Ticketmaster weigert de sleutel (HTTP {e.code})")   # nooit de URL met sleutel tonen
            last = f"HTTP {e.code}"
        except Exception as e:
            last = type(e).__name__
        time.sleep(2 * (i + 1))
    raise TMError(f"Ticketmaster niet bereikbaar ({last})")


def _window(a, b, key, out):
    """Alle events tussen a en b (datetimes). De API geeft maximaal 1000 resultaten per zoekvraag: zo nodig splitsen."""
    base = {"countryCode": "NL", "segmentId": MUSIC, "size": 200, "sort": "date,asc", "locale": "*",
            "startDateTime": a.strftime("%Y-%m-%dT%H:%M:%SZ"), "endDateTime": b.strftime("%Y-%m-%dT%H:%M:%SZ")}
    first = _get({**base, "page": 0}, key)
    total = (first.get("page") or {}).get("totalElements", 0)
    if total > 1000 and (b - a) > timedelta(days=1):
        mid = a + (b - a) / 2
        _window(a, mid, key, out); _window(mid, b, key, out)
        return
    out += (first.get("_embedded") or {}).get("events", [])
    for p in range(1, min((total + 199) // 200, 5)):
        time.sleep(0.25)
        out += (_get({**base, "page": p}, key).get("_embedded") or {}).get("events", [])


def fetch_all(key, days=600):
    raw, a = [], datetime.combine(date.today(), datetime.min.time())
    end = a + timedelta(days=days)
    while a < end:
        b = min(a + timedelta(days=31), end)
        _window(a, b, key, raw)
        a = b
        time.sleep(0.25)
    return raw


def convert(raw, have):
    """raw: Ticketmaster-events; have: lijst van onze eigen events (alle zalen) om dubbelen te vermijden.
    Geeft (events per venue-key, venues-info)."""
    by_day = {}
    for e in have:
        by_day.setdefault(e["d"], []).append(norm(e["n"]))

    def dup(d, n):
        n1 = norm(n.split(" + ")[0].split(" - ")[0].split(":")[0]) or norm(n)
        for o in by_day.get(d, []):
            if n1 and o and (n1 in o or o in n1) and min(len(n1), len(o)) >= 4:
                return True
        return False

    out, venues, seen, skipped = {}, {}, set(), {"eigen zaal": 0, "dubbel": 0, "geen concert": 0, "geannuleerd": 0}
    for x in raw:
        name = (x.get("name") or "").strip()
        st = ((x.get("dates") or {}).get("status") or {}).get("code", "")
        start = (x.get("dates") or {}).get("start") or {}
        d = start.get("localDate")
        vs = (x.get("_embedded") or {}).get("venues") or [{}]
        v = vs[0]
        if (v.get("country") or {}).get("countryCode", "NL") != "NL" or not d or not name: continue
        if st in ("cancelled", "postponed"): skipped["geannuleerd"] += 1; continue
        if JUNK.search(name): skipped["geen concert"] += 1; continue
        cl = (x.get("classifications") or [{}])[0]
        genre = " / ".join(n for n in ((cl.get("genre") or {}).get("name", ""), (cl.get("subGenre") or {}).get("name", "")) if n and n != "Undefined")
        if SKIP_GENRES.search(genre): skipped["genre"] = skipped.get("genre", 0) + 1; continue
        vname = (v.get("name") or "").strip() or "Onbekende locatie"
        city = ((v.get("city") or {}).get("name") or "").strip()
        vn = norm(vname)
        if HOSPITALITY.search(vname): skipped["geen concert"] += 1; continue
        if any(o in vn for o in OWN): skipped["eigen zaal"] += 1; continue
        k = (vn, d, norm(name))
        if k in seen: continue
        seen.add(k)
        if dup(d, name): skipped["dubbel"] += 1; continue
        key = "tm-" + slug(vname)
        venues[key] = {"label": vname, "city": city, "home": v.get("url") or "", "src": "ticketmaster"}
        out.setdefault(key, []).append({"v": key, "d": d, "n": re.sub(r"\s+", " ", name), "u": x.get("url") or "",
                                        "t": (start.get("localTime") or "")[:5], "r": city, "s": False, "c": False, "g": genre})
        by_day.setdefault(d, []).append(norm(name))
    print("ticketmaster overgeslagen:", skipped)
    return out, venues
