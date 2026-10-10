"""Tweede uitbreiding (oktober 2026): Luxor Live, Willem Twee (W2), Gigant, Fluor, De Vorstin, P3, De Meester, OCCII,
Cinetol, Groene Engel, Backstage Bridges (Heyhoef-Backstage), Muziekgieterij en Maassilo. Alles van de eigen sites."""
import json, re
from common import *
from venues6 import _from_urls, _links, tribe, stager, UA_PLAIN

# key: (lijstpagina's, patroon voor concertpagina's, naam die van de paginatitel af moet)
SITES = {
    "luxor": (["https://www.luxorlive.nl/agenda/"], r"luxorlive\.nl/agenda/[^/]+/?$", "Luxor Live|Luxor"),
    "w2": (["https://www.willem-twee.nl/alle-activiteiten"], r"willem-twee\.nl/alle-activiteiten/[^/]+$", "Willem Twee|W2"),
    "gigant": (["https://www.gigant.nl/concerten/"], r"gigant\.nl/concert/[^/]+/?$", "Gigant|Concerten|Muziekcaf|Locatie|Poppodium"),
    "vorstin": (["https://vorstin.nl/agenda/"], r"vorstin\.nl/agenda/[^/]+/?$", "De Vorstin|Vorstin"),
    "p3": (["https://www.p3purmerend.nl/programma/"], r"p3purmerend\.nl/programma/[^/]+/?$", "P3"),
    "meester": (["https://poppodiumdemeester.nl/"], r"poppodiumdemeester\.nl/event/[^/]+/?$", "De Meester|Poppodium De Meester"),
    "occii": (["https://occii.org/events/"], r"occii\.org/events/[^/]+/?$", "OCCII"),
    "cinetol": (["https://www.cinetol.nl/programma"], r"cinetol\.nl/events/[^/]+/?$", "Cinetol"),
    "engel": (["https://www.groene-engel.nl/programma/"], r"groene-engel\.nl/programma/[^/]+/?$", "De Groene Engel|Groene Engel"),
    "bridges": (["https://www.backstagebridges.nl/programma/"], r"backstagebridges\.nl/progr?amma/[^/]+/?$", "Backstage Bridges|Backstage"),
}
BASES = {k: re.match(r"https?://[^/]+", v[0][0]).group(0) for k, v in SITES.items()}


def _site(key):
    pages, pat, strip = SITES[key]
    urls = []
    for p in pages:
        for u in _links(fetch(p), BASES[key], pat):
            if u not in urls and not re.search(r"/(agenda|programma|concerten|events|alle-activiteiten|feed|navigate)/?$", u):
                urls.append(u)
    return _from_urls(key, urls, strip)


def luxor(): return _site("luxor")
def w2():   # Willem Twee is ook kunstcentrum: alleen wat in het poppodium is
    return [e for e in _site("w2") if not re.search(r"kunst|expo|atelier", e["r"], re.I)]
def gigant(): return _site("gigant")
def vorstin(): return _site("vorstin")
def p3(): return _site("p3")
def meester(): return _site("meester")
def occii(): return _site("occii")
def cinetol(): return _site("cinetol")
def engel(): return _site("engel")
def bridges(): return _site("bridges")


def fluor():
    return tribe("fluor", "https://fluor033.nl")


def muziekgieterij():
    """Schema.org op hun homepage; de tijden zijn echte UTC (de eigen ticketwinkel bevestigt: 18:00+00:00 = 20:00)."""
    from datetime import datetime
    from zoneinfo import ZoneInfo
    out = []
    for o in ld_events(fetch("https://muziekgieterij.nl/")):
        if cancelled(o): continue
        try:
            dt = datetime.fromisoformat(o["startDate"]).astimezone(ZoneInfo("Europe/Amsterdam"))
        except (KeyError, ValueError):
            continue
        d, t = dt.date().isoformat(), dt.strftime("%H:%M")
        offers = o.get("offers") or {}
        offers = offers[0] if isinstance(offers, list) and offers else offers
        u = (o.get("url") or (offers or {}).get("url") or "").split("?")[0]
        if d and o.get("name") and u:
            out.append(ev("muziekgieterij", d, o["name"], u, t, (o.get("location") or {}).get("name", ""), sold_from_offers(o)))
    return out


def maassilo():
    urls, page = [], 1
    while page <= 5:
        try:
            j = json.loads(fetch(f"https://maassilo.com/wp-json/wp/v2/event?per_page=100&page={page}", headers=UA_PLAIN))
        except RuntimeError:
            break
        urls += [x["link"] for x in j if x.get("link")]
        if len(j) < 100: break
        page += 1
    return _from_urls("maassilo", urls, "Maassilo")


# ---------- Poppodium Volt (Sittard), De Kade (Zaandam): lijstpagina + detailpagina's ----------
def volt():
    urls = [u.split("?")[0] for u in _links(fetch("https://www.poppodium-volt.nl/programma"), "https://www.poppodium-volt.nl",
                                            r"poppodium-volt\.nl/activiteit/[^/]+$")]
    urls = list(dict.fromkeys(urls))
    return _from_urls("volt", urls, "Poppodium Volt|Volt")


def kade():
    urls = _links(fetch("https://dekadezaandam.nl/agenda/"), "https://dekadezaandam.nl", r"dekadezaandam\.nl/evenementen/[^/]+/?$")
    return _from_urls("kade", urls, "De Kade|Poppodium De Kade")


# ---------- Nieuwe Nor (Heerlen): datum staat in het adres ----------
def nor():
    h = fetch("https://nieuwenor.nl/programma")
    urls = list(dict.fromkeys(re.findall(r'href="(https://nieuwenor\.nl/programma/(20\d\d)/(\d\d)/(\d\d)/[a-z0-9-]+)"', h)))
    out = _from_urls("nor", [u[0] for u in urls], "Nieuwe Nor")
    byurl = {u[0]: f"{u[1]}-{u[2]}-{u[3]}" for u in urls}
    for e in out:            # de datum uit het adres is leidend
        e["d"] = byurl.get(e["u"], e["d"])
    # de site toont ongeveer een maand vooruit; de eigen ticketwinkel vult aan
    norm = lambda t: re.sub(r"[^a-z0-9]+", "", t.lower())[:12]
    have = {(e["d"], norm(e["n"])) for e in out}
    try:
        for e in stager("nor", "nieuwenor.stager.co", "Heerlen"):
            if (e["d"], norm(e["n"])) not in have:
                out.append(e)
    except Exception as ex:
        print("nieuwe nor stager:", ex)
    return out


# ---------- Annabel (Rotterdam): agenda met labels Concert / Club ----------
WD_NL = {"maandag": 0, "dinsdag": 1, "woensdag": 2, "donderdag": 3, "vrijdag": 4, "zaterdag": 5, "zondag": 6}


def annabel():
    from venues6 import _infer
    h = fetch("https://annabel.nu/agenda/")
    out, seen = [], set()
    for m in re.finditer(r'terms-list-item">\s*([^<]+?)\s*<(.*?)elementor-button-link[^>]*href="(https://annabel\.nu/[^"]+)"', h, re.S):
        kind, block, url = m.group(1).strip().lower(), m.group(2), m.group(3)
        if kind != "concert" or url in seen: continue
        dm = re.search(r"\b(maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag)\s+(\d{1,2})\s+([a-z]+)", block)
        tm = re.search(r"<h2[^>]*>(.*?)</h2>", block, re.S)
        if not (dm and tm) or not NL_MONTHS.get(dm.group(3)): continue
        d = _infer(WD_NL[dm.group(1)], int(dm.group(2)), NL_MONTHS[dm.group(3)])
        if not d: continue
        seen.add(url)
        out.append(ev("annabel", d, clean(re.sub(r"<[^>]+>", " ", tm.group(1))), url, "", "", "uitverkocht" in block.lower()))
    return out
