"""Oktober 2026, ronde 3: Bitterzoet (Amsterdam), So What! (Gouda), Corneel (Lelystad), Kroepoekfabriek (Vlaardingen),
De Cacaofabriek (Helmond), WORM en Maassilo (Rotterdam), Carré (Amsterdam) en The Lock Keepers (Maassluis).
Alles van de eigen sites; concertpagina's lezen met de gedeelde paginalezer uit venues6 (met geheugen)."""
import re
from common import *
from venues6 import _from_urls, _links

# key: (lijstpagina's, patroon voor concertpagina's, naam die van de paginatitel af moet)
SITES = {
    "bitterzoet": (["https://www.bitterzoet.com/agenda/", "https://www.bitterzoet.com/"], r"bitterzoet\.com/event/[^/]+/?$", "Bitterzoet"),
    "sowhat": (["https://www.so-what.nl/agenda/", "https://www.so-what.nl/"], r"so-what\.nl/event/[^/]+/?$", "Poppodium So What!|So What!|So What"),
    "kroepoek": (["https://www.kroepoekfabriek.nl/agenda/"], r"kroepoekfabriek\.nl/agenda/[^/]+/?$", "Poppodium De Kroepoekfabriek|De Kroepoekfabriek|Kroepoekfabriek"),
    "cacao": (["https://www.cacaofabriek.nl/agenda?type=concert"] + [f"https://www.cacaofabriek.nl/agenda?type=concert&page={n}" for n in range(2, 6)],
              r"cacaofabriek\.nl/agenda/[a-z0-9-]+-\d\d-\d\d-20\d\d$", "De Cacaofabriek|Cacaofabriek"),   # alleen concerten, geen films
    "maassilo": (["https://maassilo.com/agenda/"], r"maassilo\.com/agenda/[^/]+/?$", "Maassilo"),
    "worm": (["https://worm.org/agenda/"], r"worm\.org/production/[^/]+/?$", "Worm|WORM"),
    "lockkeepers": (["https://thelockkeepers.nl/Concert-agenda-The-Lock-Keepers/", "https://thelockkeepers.nl/"],
                    r"thelockkeepers\.nl/Concert-agenda/[^/]+/?$", "The Lock Keepers Maassluis|The Lock Keepers|Lock Keepers"),
    "carre": (["https://carre.nl/sitemap.xml"], r"carre\.nl/voorstelling/[^/]+/?$", "Koninklijk Theater Carré|Carré"),
}
BASES = {k: re.match(r"https?://[^/]+", v[0][0]).group(0) for k, v in SITES.items()}


def _site(key, limit=150):
    pages, pat, strip = SITES[key]
    urls = []
    for p in pages:
        try:
            page = fetch(p)
        except Exception as ex:
            print(key, "lijstpagina mislukt", p, ex); continue
        found = _links(page, BASES[key], pat) + [l for l in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", page) if re.search(pat, l)]
        for u in found:
            if u not in urls and not re.search(r"/(agenda|programma|events|koop-ticket)/?$", u):
                urls.append(u)
    return _from_urls(key, urls, strip, limit=limit)


def bitterzoet():   # clubnachten (deuren na 23:00) en afgelaste avonden niet
    out = []
    for e in _site("bitterzoet"):
        e["n"] = re.sub(r"\s*[·|–-]\s*Bitterzoet\s*$", "", e["n"])
        if re.search(r"cancel+ed|afgelast", e["n"], re.I) or re.search(r"(2[3-9]|0\d):\d\d$", e.get("t", "")): continue
        out.append(e)
    return out
def sowhat(): return _site("sowhat")
def kroepoek(): return _site("kroepoek")
def cacao():   # titel zonder de datum erachter ('Robben Ford (US) | zo 18 okt 2026')
    out = _site("cacao")
    for e in out: e["n"] = re.sub(r"\s*\|\s*(ma|di|wo|do|vr|za|zo)\w* \d{1,2} \w+ 20\d\d\s*$", "", e["n"], flags=re.I)
    return out
def maassilo():
    """Maassilo is ook dance: alleen wat Maassilo zelf als concert, rock, hiphop of afrobeat aanmerkt (genrefilter van hun agenda)."""
    from datetime import date
    mons = {"jan": 1, "feb": 2, "mrt": 3, "mar": 3, "apr": 4, "mei": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "okt": 10, "nov": 11, "dec": 12}
    out, seen, today = [], set(), date.today()
    for g in ("concert", "rock", "hiphop", "afro-beat"):
        page = fetch("https://maassilo.com/agenda/?genre%5B%5D=" + g)
        for m in re.finditer(r'href="?(https://maassilo\.com/agenda/[^\s">]+)"?[^>]*>\s*<div class="?x-core-title"?>\s*<span class="?x-core-title--pre"?>\s*(\d{1,2}) ([a-z]{3})[a-z]*\s*</span>\s*<span class="?x-core-title--title"?>([^<]+)</span>', page):
            u, dd, mm, title = m.group(1), int(m.group(2)), mons.get(m.group(3).lower()), html.unescape(m.group(4)).strip()
            if not mm or u in seen: continue
            seen.add(u)
            y = today.year if (mm, dd) >= (today.month, today.day) else today.year + 1      # het jaar staat er niet bij
            out.append(ev("maassilo", date(y, mm, dd).isoformat(), title, u))
    return out
def lockkeepers():
    """The Lock Keepers (Maassluis): naam en datum staan in de link, bv. /Concert-agenda/The-Rusty-Zippers-15-oktober/."""
    from datetime import date
    mons = {"januari": 1, "februari": 2, "maart": 3, "april": 4, "mei": 5, "juni": 6, "juli": 7, "augustus": 8, "september": 9, "oktober": 10, "november": 11, "december": 12}
    out, seen, today = [], set(), date.today()
    for p in SITES["lockkeepers"][0]:
        for slug in re.findall(r'href="(?:https://thelockkeepers\.nl)?/Concert-agenda/([^/"]+)/?"', fetch(p)):
            m = re.match(r"(.+?)-(\d{1,2})-(" + "|".join(mons) + r")(?:-(\d{4,5}))?$", slug, re.I)   # '20227' (tikfout op de site): dan het eerstvolgende jaar
            if not m or slug in seen: continue
            seen.add(slug)
            dd, mm = int(m.group(2)), mons[m.group(3).lower()]
            y = int(m.group(4)) if m.group(4) and m.group(4).startswith("20") and len(m.group(4)) == 4 else (today.year if (mm, dd) >= (today.month, today.day) else today.year + 1)
            try: d = date(y, mm, dd).isoformat()
            except ValueError: continue
            out.append(ev("lockkeepers", d, m.group(1).replace("-", " "), "https://thelockkeepers.nl/Concert-agenda/" + slug + "/"))
    return out
def carre(): return _site("carre", limit=80)


def worm():
    """WORM is ook film, kunst en lezingen: alleen wat WORM zelf als 'Concert' aanmerkt (bv. 'Concert - Thu 29 October 2026')."""
    import json, os
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "worm_types.json")
    try: kinds = json.load(open(path, encoding="utf-8"))
    except Exception: kinds = {}
    pages, pat, strip = SITES["worm"]
    urls = [u for u in _links(fetch(pages[0]), BASES["worm"], pat)]
    keep = []
    for u in dict.fromkeys(urls):
        if u not in kinds:
            try:
                t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fetch(u, tries=1)))
                m = re.search(r"([A-Z][A-Za-z &/]{2,30}) - (?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\w* \d{1,2} [A-Z][a-z]+ 20\d\d", t)
                kinds[u] = m.group(1).strip() if m else ""
            except Exception:
                continue
            time.sleep(0.5)
        if re.search(r"concert|live|music|muziek", kinds[u], re.I): keep.append(u)
    json.dump({u: k for u, k in kinds.items() if u in urls}, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    return _from_urls("worm", keep, strip)


def corneel():   # de agenda van Corneel heeft schema.org-gegevens per voorstelling
    out = []
    for o in ld_events(fetch("https://www.corneel.nl/agenda/")):
        if cancelled(o): continue
        d, t = str(o.get("startDate", ""))[:10], str(o.get("startDate", ""))[11:16]
        if not re.match(r"\d{4}-\d\d-\d\d$", d): continue
        out.append(ev("corneel", d, html.unescape(o.get("name", "")), o.get("url") or "https://www.corneel.nl/agenda/", t, "", sold_from_offers(o)))
    return out
