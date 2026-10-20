"""Zelfherstel: levert een zaal ineens niets meer op (meestal omdat de zaal haar site heeft omgebouwd),
dan zoeken we zelf de concertpagina's op de eigen site van de zaal.

- Startpunt: het adres van de zaal uit docs/app.js, plus de agenda-/programmapagina's die daar gelinkt staan
  en de sitemap van de zaal.
- Concertpagina's herkennen we aan een groep van minstens 5 links met hetzelfde begin (bv. /agenda/<naam>/).
- Elke pagina wordt gelezen met de gewone paginalezer (datum, titel, tijd); alleen toekomstige concerten tellen.
- Wat gevonden is, staat in data/heal.json, zodat de ochtendcontrole kan melden welke zaal zichzelf hersteld heeft.
"""
import json, os, re
from collections import OrderedDict
from datetime import date
from urllib.parse import urljoin, urlparse
from common import fetch
from venues6 import _from_urls

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")
AGENDA = re.compile(r"agenda|programma|program|concert|events?|kalender|calendar|shows?|line-?up|voorstellingen", re.I)
SKIP = re.compile(r"/(contact|over|about|nieuws|news|blog|privacy|cookie|vacature|jobs?|login|account|mijn|winkel|shop|cart|"
                  r"verhuur|zaalverhuur|faq|info|nieuwsbrief|newsletter|tag|tags|category|categorie|author|page|zoeken|search|"
                  r"wp-content|wp-json|feed|cdn-cgi)(/|$)|\.(jpe?g|png|gif|svg|webp|pdf|css|js|xml|ico)$", re.I)


def venue_info(key):
    src = open(os.path.join(ROOT, "docs", "app.js"), encoding="utf-8").read()
    m = re.search(r"\b" + re.escape(key) + r':\{label:"([^"]*)",home:"([^"]*)"[^}]*\}', src)
    if not m:
        return None
    return {"label": m.group(1), "home": m.group(2), "fest": "fest:true" in m.group(0)}


def _links(page, url, host):
    out = []
    for href, text in re.findall(r'<a\b[^>]*href="([^"#]+)"[^>]*>(.*?)</a>', page, re.I | re.S):
        u = urljoin(url, href.strip()).split("?")[0]
        p = urlparse(u)
        if p.scheme.startswith("http") and p.hostname and p.hostname.replace("www.", "") == host:
            out.append((u, re.sub(r"<[^>]+>", " ", text)))
    return out


def discover(key, max_pages=60):
    """Toekomstige concerten van deze zaal via zelf gevonden concertpagina's; [] als het niet lukt."""
    info = venue_info(key)
    if not info or info["fest"]:
        return []
    home = info["home"]
    host = (urlparse(home).hostname or "").replace("www.", "")
    base = "{0.scheme}://{0.netloc}".format(urlparse(home))
    pages, cand = [home], OrderedDict()
    try:
        hp = fetch(home, tries=2, timeout=30)
    except Exception as ex:
        print(key, "zelfherstel: startpagina mislukt", ex)
        return []
    for u, text in _links(hp, home, host):
        if (AGENDA.search(text) or AGENDA.search(urlparse(u).path)) and u not in pages and len(pages) < 4:
            pages.append(u)
    lists = [hp]
    for u in pages[1:]:
        try:
            lists.append(fetch(u, tries=2, timeout=30))
        except Exception:
            pass
    for pg, u in zip(lists, pages):
        for l, _ in _links(pg, u, host):
            cand[l] = 1
    try:   # sitemap: vaak staan alle concertpagina's erin
        sm = fetch(base + "/sitemap.xml", tries=1, timeout=20)
        locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", sm)
        subs = [l for l in locs if l.endswith(".xml") and AGENDA.search(l)][:3]
        for s in subs:
            try:
                locs += re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", fetch(s, tries=1, timeout=20))
            except Exception:
                pass
        for l in locs:
            if not l.endswith(".xml") and (urlparse(l).hostname or "").replace("www.", "") == host:
                cand[l.split("?")[0]] = 1
    except Exception:
        pass
    # groeperen op alles behalve het laatste stuk van het pad: /agenda/<concert>/ -> /agenda/
    groups = {}
    for u in cand:
        path = urlparse(u).path
        if SKIP.search(path):
            continue
        parts = [p for p in path.split("/") if p]
        if len(parts) < 2 or len(parts[-1]) < 4 or not re.search(r"[a-z]", parts[-1], re.I):
            continue
        groups.setdefault("/" + "/".join(parts[:-1]) + "/", []).append(u)
    groups = sorted(((p, us) for p, us in groups.items() if len(us) >= 5), key=lambda x: -len(x[1]))
    today = date.today().isoformat()
    for prefix, urls in groups[:2]:
        got = [e for e in _from_urls(key, urls[:max_pages], info["label"], limit=max_pages) if e["d"] >= today]
        me = re.sub(r"[^a-z0-9]", "", (info["label"] + host).lower())
        for e in got:   # zaalnaam achter de titel weg: 'Wende | Nobel'
            m = re.search(r"\s+[|–-]\s+([^|–-]{2,30})$", e["n"])
            if m and re.sub(r"[^a-z0-9]", "", m.group(1).lower()) in me:
                e["n"] = e["n"][:m.start()].strip()
        if len(got) >= 3:
            note(key, base + prefix, len(got))
            print(f"{key}: zelfherstel gelukt via {base + prefix} ({len(got)} concerten)")
            return got
    print(key, "zelfherstel: geen concertpagina's gevonden")
    return []


def note(key, prefix, n):
    p = os.path.join(DATA, "heal.json")
    try:
        h = json.load(open(p, encoding="utf-8"))
    except Exception:
        h = {}
    h[key] = {"at": date.today().isoformat(), "via": prefix, "count": n}
    json.dump(h, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
