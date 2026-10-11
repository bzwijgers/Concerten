"""België (oktober 2026): AB, Botanique, Trix, De Roma, Het Depot, Handelsbeurs, Cactus, De Kreun (Wilde Westen), 4AD, N9,
De Casino, Reflektor en Het Bos. Alles van de eigen sites (of hun eigen ticketwinkel)."""
import re
from common import *
from venues6 import _from_urls, _links, stager

# key: (lijstpagina's, patroon voor concertpagina's, naam die van de paginatitel af moet)
SITES = {
    "ab": (["https://www.abconcerts.be/nl/agenda"], r"abconcerts\.be/nl/agenda/[^/]+/[A-Za-z0-9]{10,}$", "Ancienne Belgique|AB"),
    "botanique": (["https://botanique.be/nl/concerts"], r"botanique\.be/nl/concert/[^/]+$", "Botanique"),
    "trix": (["https://www.trixonline.be/nl/programma"], r"trixonline\.be/nl/event/[^/]+$", "Trix"),
    "roma": (["https://www.deroma.be/nl/", "https://www.deroma.be/nl/agenda"], r"deroma\.be/nl/event/[^/]+$", "De Roma"),
    "depot": (["https://www.hetdepot.be/programma"], r"hetdepot\.be/concert/20\d\d/[^/]+$", "Het Depot"),
    "ha": (["https://www.haconcerts.be/nl/concertagenda"], r"haconcerts\.be/nl/concertagenda/concerten/[^/]+$", "Handelsbeurs|HA Concerts"),
    "kreun": (["https://www.wildewesten.be/nl/agenda"], r"wildewesten\.be/nl/event/[^/]+$", "Wilde Westen|De Kreun"),
    "n9": (["https://www.n9.be/agenda/"], r"n9\.be/agenda/\d+-[^/]+/?$", "N9"),
    "casino": (["https://decasino.be/"], r"decasino\.be/concert/[^/]+/?$", "De Casino"),
    "reflektor": (["https://reflektor.be/agenda/"], r"reflektor\.be/nl/concert/[^/]+/?$", "Reflektor"),
    "bos": (["https://www.hetbos.be/programma"], r"hetbos\.be/programma/evenement/[^/]+/?$", "Het Bos"),
}
BASES = {k: re.match(r"https?://[^/]+", v[0][0]).group(0) for k, v in SITES.items()}
# agenda's met paginering: (eerste paginanummer, maximum)
PAGED = {"ab": (2, 30), "trix": (2, 10), "depot": (1, 12), "kreun": (1, 10)}
# agenda's waarvan de sitemap alle concertpagina's bevat
SITEMAP = {"ha": "https://www.haconcerts.be/sitemap.xml", "reflektor": "https://reflektor.be/sitemap.xml"}


def _site(key):
    pages, pat, strip = SITES[key]
    urls = []
    def add(h):
        new = [u for u in _links(h, BASES[key], pat) if u not in urls]
        urls.extend(new)
        return len(new)
    for p in pages:
        try:
            add(fetch(p))
        except Exception as ex:
            print(key, "lijstpagina mislukt", p, ex)
    if key in PAGED:
        first, last = PAGED[key]
        for n in range(first, last + 1):
            try:
                if not add(fetch(pages[0] + ("&" if "?" in pages[0] else "?") + "page=" + str(n))): break
            except Exception:
                break
            time.sleep(0.5)
    if key in SITEMAP:
        try:
            sm = fetch(SITEMAP[key]); locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", sm)
            for sub in [l for l in locs if l.endswith(".xml")][:20]:
                locs += re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", fetch(sub))
            for l in locs:
                if key == "reflektor": l = l.replace("reflektor.be/concert/", "reflektor.be/nl/concert/")   # Nederlandstalige pagina
                if re.search(pat, l) and l not in urls: urls.append(l)
        except Exception as ex:
            print(key, "sitemap mislukt", ex)
    return _from_urls(key, urls, strip, limit=250)


def ab(): return _site("ab")
def botanique(): return _site("botanique")
def trix(): return _site("trix")
def roma(): return _site("roma")
def depot(): return _site("depot")
def ha(): return _site("ha")
def kreun(): return _site("kreun")
def n9(): return _site("n9")
def casino(): return _site("casino")
def reflektor(): return _site("reflektor")
def bos(): return _site("bos")
def vierad(): return stager("vierad", "muziekclub4ad.stager.co", "Diksmuide")
