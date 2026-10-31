"""Oktober 2026, ronde 3: Bitterzoet (Amsterdam), So What! (Gouda), Corneel (Lelystad), Kroepoekfabriek (Vlaardingen),
De Cacaofabriek (Helmond), WORM en Maassilo (Rotterdam), Carré (Amsterdam) en The Lock Keepers (Maassluis).
Alles van de eigen sites; concertpagina's lezen met de gedeelde paginalezer uit venues6 (met geheugen)."""
import re
from common import *
from venues6 import _from_urls, _links

# key: (lijstpagina's, patroon voor concertpagina's, naam die van de paginatitel af moet)
SITES = {
    "bitterzoet": (["https://www.bitterzoet.com/agenda/", "https://www.bitterzoet.com/"], r"bitterzoet\.com/event/[^/]+/?$", "Bitterzoet"),
    "sowhat": (["https://www.so-what.nl/agenda/", "https://www.so-what.nl/"], r"so-what\.nl/(?:event|agenda)/[^/]+/?$", "Poppodium So What!|So What!|So What"),
    "kroepoek": (["https://www.kroepoekfabriek.nl/agenda/", "https://kroepoekfabriek.nl/agenda/feed/"] + [f"https://kroepoekfabriek.nl/agenda/feed/?paged={n}" for n in range(2, 5)], r"kroepoekfabriek\.nl/agenda/[^/]+/?$", "Poppodium De Kroepoekfabriek|De Kroepoekfabriek|Kroepoekfabriek"),
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
        found = _links(page, BASES[key], pat) + [l for l in re.findall(r"<(?:loc|link)>\s*([^<\s]+)\s*</(?:loc|link)>", page) if re.search(pat, l)]
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
def sowhat():   # sinds okt 2026 staan ook lidmaatschap en bierverkoop in hun agenda
    return [e for e in _site("sowhat") if not re.search(r"lidmaatschap|craftbeer|adventskalender|karao", e["n"], re.I)]
def kroepoek():   # agenda is JS-pagina; de feed noemt de komende evenementen
    out = _site("kroepoek")
    for e in out: e["n"] = re.sub(r"\s*[-–|]\s*Kroepoekfabriek\s*$", "", e["n"])
    return out
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
    """The Lock Keepers (Maassluis): de agendapagina noemt elk concert als tekst, bv.
    '29-4-2027. Jim Keller met band ( donderdag 20.30, ...'. Heeft het concert een eigen pagina, dan linken we die."""
    from datetime import date
    agenda = "https://thelockkeepers.nl/Concert-agenda-The-Lock-Keepers/"
    page = fetch(agenda)
    links = re.findall(r'href="(?:https://thelockkeepers\.nl)?(/Concert-agenda/[^"/]+/?)"', page)
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", page)))
    out = []
    for dd, mm, yy, title, hh, mi in re.findall(r"\b(\d{1,2})-(\d{1,2})-(20\d\d)\. ([^(]{3,90}?)\s*\(\s*[a-z]+ (\d{1,2})[.:](\d\d)", text):
        try: d = date(int(yy), int(mm), int(dd)).isoformat()
        except ValueError: continue
        title = title.strip(" .,")
        words = [w for w in re.findall(r"[a-z]{4,}", title.lower())][:2]
        own = [l for l in links if words and all(w in l.lower() for w in words)]
        out.append(ev("lockkeepers", d, title, "https://thelockkeepers.nl" + own[0] if own else agenda, f"{int(hh):02d}:{mi}"))
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


# Vessel 11 (Rotterdam, schip in de Wijnhaven): ook spelletjes, comedy, swing en open decks; die laten we weg
SITES["v11"] = (["https://www.vessel11.nl/nl/agenda/", "https://www.vessel11.nl/nl/"], r"vessel11\.nl/nl/events/[^/]+/?$", "Vessel 11|V11")
BASES["v11"] = "https://www.vessel11.nl"
V11_NOT = re.compile(r"board ?game|comedy|jokes|open decks|swing|quiz|karaoke|bingo|halloween|silent disco|workshop|markt|market|yoga|lezing|dance ?class|salsa", re.I)


def v11():
    return [e for e in _site("v11") if not V11_NOT.search(e["n"] + " " + e["u"])]


def manifesto():
    """Manifesto (Hoorn): de RSS-feed 'upcoming_events' van hun site, met per evenement titel, link en datum in de tekst."""
    from datetime import date
    mons = {"januari": 1, "februari": 2, "maart": 3, "april": 4, "mei": 5, "juni": 6, "juli": 7, "augustus": 8,
            "september": 9, "oktober": 10, "november": 11, "december": 12}
    feed = fetch("https://manifesto-hoorn.nl/upcoming_events")
    out = []
    for item in re.findall(r"<item>(.*?)</item>", feed, re.S):
        title = html.unescape(re.sub(r"<!\[CDATA\[|\]\]>", "", (re.search(r"<title>(.*?)</title>", item, re.S) or [None, ""])[1])).strip()
        link = (re.search(r"<link>\s*([^<\s]+)", item) or [None, "https://manifesto-hoorn.nl/"])[1]
        body = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", html.unescape(re.sub(r"<!\[CDATA\[|\]\]>", " ", item)))))
        m = re.search(r"\b(\d{1,2}) (" + "|".join(mons) + r") (20\d\d)\b", body, re.I)
        if not title or not m: continue
        t = re.search(r"(?:aanvang|tijd:?|start)\s*(\d{1,2})[.:](\d\d)", body, re.I)
        out.append(ev("manifesto", date(int(m.group(3)), mons[m.group(2).lower()], int(m.group(1))).isoformat(), title, link,
                      f"{int(t.group(1)):02d}:{t.group(2)}" if t else "", "", bool(re.search(r"uitverkocht", title, re.I))))
    return [e for e in out if not re.search(r"quiz|open mic|bingo|karaoke|club festo|haunted|spookhuis|kom en dans|burlesque", e["n"], re.I)]


# CAPSLOC (Capelle aan den IJssel)
SITES["capsloc"] = (["https://www.capsloc.nl/programma/"], r"capsloc\.nl/programma/[a-z0-9-]+/?$", "CAPSLOC|Capsloc")
BASES["capsloc"] = "https://www.capsloc.nl"


def capsloc():
    return [e for e in _site("capsloc") if not re.search(r"/feed/?$", e["u"])]


# LantarenVenster (Rotterdam): de muziekpagina met alle concerten; datum en tijd uit de detailpagina's (ld+json)
SITES["lantaren"] = (["https://www.lantarenvenster.nl/muziek/"], r"lantarenvenster\.nl/programma/[a-z0-9-]+/?$", r"\s*-\s*LantarenVenster.*$|LantarenVenster Rotterdam")
BASES["lantaren"] = "https://www.lantarenvenster.nl"


def lantaren():
    return [e for e in _site("lantaren", limit=200) if not re.search(r"/feed/?$|yoga|cinekid|boekpresentatie|filmprogramma|muziekfilms|salsa-aan-de-haven", e["u"])]


def studiogonz():
    """StudioGonz (Gouda): de agendapagina met per concert dag, maand en titel; het jaar staat er niet bij.
    Geen quiz, karaoke, comedy, yoga of besloten feest (dat filtert main.py grotendeels ook)."""
    from datetime import date
    mons = {"jan": 1, "feb": 2, "mrt": 3, "mar": 3, "apr": 4, "mei": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "okt": 10, "nov": 11, "dec": 12}
    page, out, today = fetch("https://www.studiogonz.nl/agenda"), [], date.today()
    for m in re.finditer(r'<a href="(/agenda/\d+/[^"]+)"><span class="date"><small>\w+</small><b>(\d{1,2})</b><small>([a-z]{3})[a-z]*\.?</small></span>.*?'
                         r'<span class="title">(.*?)<span class="subtitle">(.*?)</span>', page, re.S):
        u, dd, mm = "https://www.studiogonz.nl" + m.group(1), int(m.group(2)), mons.get(m.group(3).lower())
        title = html.unescape(re.sub(r"<[^>]+>|\s+", " ", m.group(4))).strip()
        if not mm or re.search(r"besloten|pubquiz|karaoke|stand-?up|comedy|yoga|speciaalbierbar", title, re.I): continue
        y = today.year if (mm, dd) >= (today.month, today.day) else today.year + 1
        sub = html.unescape(re.sub(r"<[^>]+>|\s+", " ", m.group(5))).strip()
        if re.search(r"metal night", title, re.I) and sub: title = sub.replace("|", " +")   # 'StudioGonz Metal Night' -> de bands
        out.append(ev("studiogonz", date(y, mm, dd).isoformat(), title, u))
    return out


def acu():
    """ACU (Utrecht): de volledige agenda; alleen wat het ACU zelf als bands, loud, noise of folkpunk aanmerkt."""
    page, out = fetch("https://www.acu.nl/agenda/"), []
    for m in re.finditer(r'<li class="AgendaEntry ([^"]*)">\s*<a href="(https://acu\.nl/events/(\d{4})(\d\d)(\d\d)/[^"]+)".*?'
                         r'<p class="overflowing pseudo-h2">(.*?)</p>(.*?)</li>\s*</ul>', page, re.S):
        if not re.search(r"\b(bands|loud|noise|folkpunk)\b", m.group(1)): continue
        t = re.search(r"Start:</span><span class=\"AgendaDetail\">(\d\d:\d\d)", m.group(7))
        out.append(ev("acu", f"{m.group(3)}-{m.group(4)}-{m.group(5)}", html.unescape(m.group(6)).strip().rstrip("."), m.group(2), t.group(1) if t else ""))
    return out


def littledevil():
    """Little Devil (Tilburg): programmalijst met datum (d-m-jjjj), titel en '20u | genre | prijs'. Geen dansavond, sport, quiz of jamsessie."""
    page, out = fetch("https://www.littledevil.nl/"), []
    for m in re.finditer(r'<a href="([^"]+\.html)" class="programma-rij-link">.*?<time class="rij-datum" datetime="(\d{1,2})-(\d{1,2})-(\d{4})">.*?'
                         r'<h2 class="rij-titel">(.*?)</h2>\s*<div class="rij-info">(.*?)</div>', page, re.S):
        title, info = html.unescape(m.group(5)).strip(), html.unescape(m.group(6))
        if re.search(r"sports|formula|quiz|jamsessie|halloween party|bat ?cave|dansavond|goth los", title + " " + info, re.I): continue
        t = re.search(r"\b(\d{1,2})(?:[:.](\d\d))?\s*u\b|\b(\d{1,2})[:.](\d\d)\b", info)
        tm = (f"{int(t.group(1)):02d}:{t.group(2) or '00'}" if t.group(1) else f"{int(t.group(3)):02d}:{t.group(4)}") if t else ""
        out.append(ev("littledevil", f"{m.group(4)}-{int(m.group(3)):02d}-{int(m.group(2)):02d}", title, "https://www.littledevil.nl/" + m.group(1).lstrip("/"), tm))
    return out


def tbeest():
    """'t Beest (Goes): de categorie 'concert' van hun agenda (WordPress Theatre: 'za 31 oktober' en '21:00'; jaar staat er niet bij)."""
    from datetime import date
    mons = {"januari": 1, "februari": 2, "maart": 3, "april": 4, "mei": 5, "juni": 6, "juli": 7, "augustus": 8, "september": 9, "oktober": 10, "november": 11, "december": 12}
    page, out, today = fetch("https://tbeest.nl/?category=concert"), [], date.today()
    for m in re.finditer(r'wpt_production_category_concert">.*?wp_theatre_event_startdate">\w+ (\d{1,2}) (\w+)</div>.*?wp_theatre_event_starttime">(\d\d:\d\d)</div>.*?'
                         r'<div class=wp_theatre_event_title><a href=(https://tbeest\.nl/productie/[^\s>]+)\s*>(.*?)</a>', page, re.S):
        mm = mons.get(m.group(2).lower())
        if not mm: continue
        dd = int(m.group(1)); y = today.year if (mm, dd) >= (today.month, today.day) else today.year + 1
        out.append(ev("tbeest", date(y, mm, dd).isoformat(), html.unescape(m.group(5)).strip(), m.group(4), m.group(3)))
    return out


def gashouder():
    """Gashouder (Amsterdam, Westergas): alleen wat de Gashouder zelf als 'live' aanmerkt (geen dance, kunst of performance).
    Programma op de voorpagina: 'DO 5 NOV', '19:00', soort en naam; meerdaagse ('ZA 31 OKT - ZO 1 NOV') op de eerste dag."""
    from datetime import date
    mons = {"jan": 1, "feb": 2, "mrt": 3, "apr": 4, "mei": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "okt": 10, "nov": 11, "dec": 12}
    page, out, seen, today = fetch("https://www.gashouder.com/"), [], set(), date.today()
    for blk in re.findall(r'<a href="/programma/.*?</a>', page, re.S):   # per concert eerst het eigen blok, dan de onderdelen
        u = re.match(r'<a href="(/programma/[^"]+)"', blk).group(1)
        d = re.search(r'data-original="\w+ (\d{1,2}) (\w{3})', blk); k = re.search(r'<span class="label-small text-neutral-500">(\w+)</span>', blk)
        h = re.search(r'<h3 data-original="([^"]+)"', blk); t = re.search(r'data-original="(\d\d:\d\d)"', blk)
        if not (d and k and h) or k.group(1) != "live" or u in seen: continue
        mm = mons.get(d.group(2).lower()); dd = int(d.group(1))
        if not mm: continue
        seen.add(u)
        y = today.year if (mm, dd) >= (today.month, today.day) else today.year + 1
        out.append(ev("gashouder", date(y, mm, dd).isoformat(), html.unescape(h.group(1)).strip(), "https://www.gashouder.com" + u, t.group(1) if t and t.group(1) >= "12:00" else ""))
    return out
