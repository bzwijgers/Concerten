import json, os, sys, traceback, importlib
from datetime import date, datetime, timedelta, timezone
sys.path.insert(0, os.path.dirname(__file__))
from common import *
import venues1, venues2, venues3

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "docs", "data")

VENUES = [  # key, label, fn
    ("baroeg", venues2.baroeg), ("rotown", venues1.rotown), ("paradiso", None), ("melkweg", venues1.melkweg),
    ("o13", venues1.o13), ("paard", venues1.paard), ("mezz", venues1.mezz), ("effenaar", venues2.effenaar),
    ("pul", venues3.pul), ("boerderij", venues1.boerderij), ("patronaat", venues2.patronaat),
    ("hedon", venues3.hedon), ("helling", venues1.helling), ("dynamo", venues1.dynamo),
]

def load(path, default):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return default

def main():
    os.makedirs(DATA, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    only = set(sys.argv[1:])
    today = date.today().isoformat()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    store = load(os.path.join(DATA, "events.json"), {"events": {}, "status": {}})
    events, status = store["events"], store.get("status", {})
    pcache = load(os.path.join(DATA, "paradiso_cache.json"), {})
    fresh = {}
    for key, fn in VENUES:
        if only and key not in only: continue
        try:
            got = venues1.paradiso(pcache) if key == "paradiso" else fn()
            got = [e for e in got if e["d"] >= today and e["d"] <= (date.today() + timedelta(days=600)).isoformat()]
            if len(got) < 3:
                raise RuntimeError(f"only {len(got)} events")
            fresh[key] = got
            status[key] = {"ok": True, "count": len(got), "at": now}
            print(f"{key}: {len(got)}")
        except Exception as ex:
            status[key] = {"ok": False, "error": str(ex)[:200], "at": status.get(key, {}).get("at"), "count": status.get(key, {}).get("count")}
            print(f"{key}: FAILED {ex}")
            traceback.print_exc()
    # merge: id = venue + date + url (stable); first_seen kept
    for key, got in fresh.items():
        ids = set()
        for e in got:
            eid = f"{e['v']}|{e['d']}|{e['u']}"
            ids.add(eid)
            old = events.get(eid)
            e["first"] = old["first"] if old else today
            e["last"] = today
            events[eid] = e
        # events of this venue no longer listed -> drop (cancelled/removed), unless past
        for eid in [k for k, v in events.items() if v["v"] == key and k not in ids]:
            del events[eid]
    # keep past events one month for the archive
    cutoff = (date.today() - timedelta(days=45)).isoformat()
    for eid in [k for k, v in events.items() if v["d"] < cutoff]:
        del events[eid]
    store = {"events": events, "status": status, "updated": now}
    json.dump(store, open(os.path.join(DATA, "events.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    json.dump(pcache, open(os.path.join(DATA, "paradiso_cache.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    pub = sorted(events.values(), key=lambda e: (e["d"], e["v"], e["n"]))
    json.dump({"updated": now, "status": status, "events": pub}, open(os.path.join(OUT, "events.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("total", len(pub))

if __name__ == "__main__":
    main()
