"""Extra poppodia: hergebruikt de bestaande, eigen-site-scrapers uit scraper/ext (afkomstig uit het bestaande project)."""
import os, re, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from ext import new_venues, bird as _bird, gebouw_t as _gt, tolhuistuin as _th
from ext.common import normalize_url


def conv(key, items):
    out = []
    for i in items:
        if not i.get("date") or not i.get("url") or not i.get("artist"): continue
        sub = i.get("venue") or ""
        out.append({"v": key, "d": i["date"], "n": i["artist"], "u": i["url"], "t": i.get("time", "") or "",
                    "r": sub if sub and sub.lower() != key else "", "s": False, "c": False})
    return out


def _nv(name, key):
    return lambda: conv(key, new_venues.scrape_venue(name))


klokgebouw = _nv("Klokgebouw", "klokgebouw")
doornroosje = _nv("Doornroosje", "doornroosje")
metropool = _nv("Metropool", "metropool")
spot = _nv("SPOT Groningen", "spot")
bibelot = _nv("Bibelot", "bibelot")
bosuil = _nv("De Bosuil", "bosuil")
bird = lambda: conv("bird", _bird.scrape_bird())
gebouwt = lambda: conv("gebouwt", _gt.scrape_gebouw_t())
tolhuistuin = lambda: conv("tolhuistuin", _th.scrape_tolhuistuin())
