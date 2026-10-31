"""Zalen die de servers van GitHub weigeren (Melkweg sinds oktober 2026) ophalen vanuit de dagelijkse ochtendcontrole
in de cloud. Schrijft data/inbox/<zaal>.json; main.py gebruikt die als reservelijst als de zaal vanaf GitHub niets geeft.
Gebruik: python tools/cloud_fetch.py melkweg"""
import json, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scraper"))
SCRAPERS = {"melkweg": ("venues1", "melkweg")}

for key in sys.argv[1:] or list(SCRAPERS):
    mod, fn = SCRAPERS[key]
    try:
        evs = getattr(__import__(mod), fn)()
    except Exception as ex:
        print(key, "mislukt:", ex); continue
    if len(evs) < 10:
        print(key, "te weinig concerten:", len(evs)); continue
    os.makedirs(os.path.join(ROOT, "data", "inbox"), exist_ok=True)
    json.dump({"format": 2, "fetched": time.strftime("%Y-%m-%dT%H:%M:%S"), "events": evs},
              open(os.path.join(ROOT, "data", "inbox", key + ".json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(key, len(evs), "concerten -> data/inbox/" + key + ".json")
