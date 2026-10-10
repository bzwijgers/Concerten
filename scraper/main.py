import json, os, sys, traceback, importlib
from datetime import date, datetime, timedelta, timezone
sys.path.insert(0, os.path.dirname(__file__))
from common import *
import venues1, venues2, venues3, venues4, venues5, venues6, venues7, feedimport, ticketmaster, tsmap, times

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "docs", "data")

VENUES = [  # key, label, fn
    ("baroeg", venues2.baroeg), ("rotown", venues1.rotown), ("paradiso", None), ("melkweg", venues1.melkweg),
    ("o13", venues1.o13), ("paard", venues1.paard), ("mezz", venues1.mezz), ("effenaar", venues2.effenaar),
    ("pul", venues3.pul), ("boerderij", venues1.boerderij), ("patronaat", venues2.patronaat),
    ("hedon", venues3.hedon), ("helling", venues1.helling), ("dynamo", venues1.dynamo),
    ("klokgebouw", venues4.klokgebouw), ("doornroosje", venues4.doornroosje), ("metropool", venues4.metropool),
    ("spot", venues4.spot), ("bibelot", venues4.bibelot), ("bosuil", venues4.bosuil), ("bird", venues4.bird),
    ("gebouwt", venues4.gebouwt), ("neushoorn", venues4.neushoorn), ("amare", venues5.amare), ("tolhuistuin", venues5.tolhuistuin),
    ("bolwerk", venues5.bolwerk), ("dbs", venues5.dbs),
    ("burgerweeshuis", venues6.burgerweeshuis), ("ekko", venues6.ekko), ("nobel", venues6.nobel), ("grenswerk", venues6.grenswerk), ("iduna", venues6.iduna), ("musicon", venues6.musicon),
    ("qfactory", venues6.qfactory), ("simplon", venues6.simplon), ("sounddog", venues6.sounddog), ("vera", venues6.vera), ("victorie", venues6.victorie),
    ("luxor", venues7.luxor), ("w2", venues7.w2), ("gigant", venues7.gigant), ("fluor", venues7.fluor), ("vorstin", venues7.vorstin), ("p3", venues7.p3),
    ("meester", venues7.meester), ("occii", venues7.occii), ("cinetol", venues7.cinetol), ("engel", venues7.engel), ("bridges", venues7.bridges), ("muziekgieterij", venues7.muziekgieterij),
    ("volt", venues7.volt), ("kade", venues7.kade), ("nor", venues7.nor), ("annabel", venues7.annabel), ("hof", venues7.hof),
]

def load(path, default):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return default

def merge_tivoli_inbox():
    """Verwerk data/inbox/tivoli.json (door de eigenaar van een eigen toestel geüpload) in data/manual/tivoli.json."""
    ib = os.path.join(DATA, "inbox", "tivoli.json")
    mp = os.path.join(DATA, "manual", "tivoli.json")
    if not os.path.exists(ib): return
    b = load(ib, None); m = load(mp, None)
    if b and b.get("format") == 2:   # van tools/tivoli_pc.py: kant-en-klare concerten
        old = (m or {}).get("events", []) if (m or {}).get("format") == 2 else []
        evs = b.get("events") or []
        if not b.get("complete"):    # onvolledige lijst: bekende concerten na de laatste nieuwe datum behouden
            last = max((e["d"] for e in evs), default="")
            evs = evs + [e for e in old if e["d"] > last]
        json.dump({"venue": "tivoli", "format": 2, "checked": (b.get("fetched") or "")[:10], "events": evs,
                   "times": b.get("times") or {}, "note": "Opgehaald op de eigen pc van de eigenaar (Tivoli laat GitHub niet toe)."},
                  open(mp, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        os.remove(ib)
        print(f"tivoli inbox verwerkt: {len(evs)} concerten")
        return
    if not b or not m or not b.get("listed"): return
    known = m.setdefault("known", {})
    for i, d in (b.get("details") or {}).items():
        known[i] = "x" if d.get("x") else (",".join(d.get("g") or []) or "?")
    old = {e["u"].split("/agenda/")[1].split("/")[0]: e for e in m["events"]}
    out = {}
    for e in b["listed"]:
        i = e["id"]
        if known.get(i) == "x": continue
        prev = old.get(i, {})
        det = (b.get("details") or {}).get(i, {})
        out[i] = {"v": "tivoli", "d": e["d"], "n": prev.get("n") or e["n"], "u": e["u"], "t": "",
                  "r": prev.get("r", ""), "s": bool(det.get("s", prev.get("s", False))), "c": False}
    if b.get("complete"):
        events = list(out.values())
    else:   # onvolledige lijst: bestaande concerten behouden
        merged = dict(old); merged.update(out); events = list(merged.values())
    m["events"] = sorted(events, key=lambda e: (e["d"], e["n"]))
    m["checked"] = (b.get("fetched") or "")[:10] or m.get("checked")
    json.dump(m, open(mp, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    smp = b.get("samples") or {}
    if smp:
        os.makedirs(os.path.join(DATA, "samples"), exist_ok=True)
        for k, v in smp.items():
            if v: open(os.path.join(DATA, "samples", f"tivoli_{k}.html"), "w", encoding="utf-8").write(v)
    os.remove(ib)
    print(f"tivoli inbox verwerkt: {len(m['events'])} concerten")


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
            if len(got) < {"tolhuistuin": 1}.get(key, 3):
                raise RuntimeError(f"only {len(got)} events")
            fresh[key] = got
            status[key] = {"ok": True, "count": len(got), "at": now}
            print(f"{key}: {len(got)}")
        except Exception as ex:
            status[key] = {"ok": False, "error": str(ex)[:200], "at": status.get(key, {}).get("at"), "count": status.get(key, {}).get("count")}
            print(f"{key}: FAILED {ex}")
            traceback.print_exc()
    merge_tivoli_inbox()
    # Tivoli komt van de eigen pc (data/manual/tivoli.json); is die lijst ouder dan 3 dagen, dan de oude feed
    tv = load(os.path.join(DATA, "manual", "tivoli.json"), {}) or {}
    tv_recent = tv.get("format") == 2 and (tv.get("checked") or "") >= (date.today() - timedelta(days=3)).isoformat()
    feed = feedimport.load()
    if feed:
        # terugval: alleen als de eigen bron vandaag niets opleverde
        for src, key, minimum in (("TivoliVredenburg", "tivoli", 50), ("dB's", "dbs", 5)):
            if key in fresh or (key == "tivoli" and tv_recent): continue
            got = [e for e in feedimport.events_for(feed, src, key) if e["d"] >= today]
            if len(got) >= minimum:
                fresh[key] = got
                status[key] = {"ok": True, "count": len(got), "at": now, "via": "oude feed (terugval)"}
                print(f"{key}: {len(got)} (feed)")
    # aanvullen met de eigen feed (zelfde zaalsites): wat de scraper hier mist, maar de feed wel heeft
    if feed:
        for key, src in (("klokgebouw", "Klokgebouw"), ("doornroosje", "Doornroosje"), ("metropool", "Metropool"),
                         ("spot", "SPOT Groningen"), ("bibelot", "Bibelot"), ("bosuil", "De Bosuil"), ("bird", "BIRD"),
                         ("gebouwt", "Gebouw-T"), ("neushoorn", "Neushoorn")):
            if key in fresh:
                seen = {feedimport.norm_url(e["u"]) for e in fresh[key]}
                extra = [e for e in feedimport.events_for(feed, src, key) if e["d"] >= today and feedimport.norm_url(e["u"]) not in seen]
                if extra:
                    print(f"{key}: +{len(extra)} uit feed")
                    fresh[key] += extra
    # Tolhuistuin: alleen concerten die niet al in het programma van Paradiso staan
    if "tolhuistuin" in fresh:
        import re as _re
        norm = lambda t: _re.sub(r"[^a-z0-9]+", "", t.lower())
        pdi = [e for e in list(events.values()) + fresh.get("paradiso", []) if e["v"] == "paradiso"]
        have = {(e["d"], norm(e["n"])) for e in pdi}
        have_d = {}
        for e in pdi: have_d.setdefault(e["d"], []).append(norm(e["n"]))
        def dup(e):
            n = norm(e["n"])
            if (e["d"], n) in have: return True
            return any(n and (n in o or o in n) and min(len(n), len(o)) >= 5 for o in have_d.get(e["d"], []))
        before = len(fresh["tolhuistuin"])
        fresh["tolhuistuin"] = [e for e in fresh["tolhuistuin"] if not dup(e)]
        print(f"tolhuistuin: {before} -> {len(fresh['tolhuistuin'])} zonder Paradiso-dubbelen")
    # handmatig bijgehouden zalen (site niet automatisch bereikbaar)
    mdir = os.path.join(DATA, "manual")
    if os.path.isdir(mdir):
        for fn_ in sorted(os.listdir(mdir)):
            if not fn_.endswith(".json"): continue
            m = load(os.path.join(mdir, fn_), None)
            if not m or m["venue"] in fresh: continue
            got = [e for e in m["events"] if e["d"] >= today]
            fresh[m["venue"]] = got
            status[m["venue"]] = {"ok": True, "manual": True, "count": len(got), "at": now, "checked": m.get("checked"), "note": m.get("note")}
            print(f"{m['venue']}: {len(got)} (handmatig)")
    # geannuleerd / verplaatst (op de oude datum) eruit; 'nieuwe datum' uit de titel halen
    import re as _re
    gone = _re.compile(r"^\s*(cancelled|canceled|geannuleerd|afgelast|verplaatst|postponed)\s*[:\-–!]"
                       r"|[\[(]\s*(cancelled|canceled|geannuleerd|afgelast|verplaatst|postponed)\s*[\])]", _re.I)
    newdate = _re.compile(r"^\s*nieuwe datum\s*[:\-–]\s*|\s*[\[(]\s*nieuwe datum\s*[\])]", _re.I)
    for key in fresh:
        before = len(fresh[key])
        fresh[key] = [e for e in fresh[key] if not gone.search(e["n"])]
        for e in fresh[key]: e["n"] = newdate.sub("", e["n"]).strip()
        if len(fresh[key]) < before: print(f"{key}: {before - len(fresh[key])} geannuleerd/verplaatst weggelaten")
    # aanvangstijden aanvullen van de eigen detailpagina's (eenmalig per concert, onthouden in data/times.json)
    try:
        times.fill(fresh, DATA)
    except Exception as ex:
        print("tijden aanvullen mislukt:", ex)
    # geen concert: quizzen, workshops, kindervoorstellingen, platenbeurs e.d. (lijst nagelopen op 2026-10-10)
    nonc = _re.compile(r"\b(pop\s*quiz|quiz|platenbeurs|jukebox|luistersessies?|workshops?|masterclass|lezing|expositie|"
                       r"rondleiding|yoga|boekenclub|podcast|science\s*caf[eé]|comedy(?!\s+of\s+errors)|stand-?up|cabaret|"
                       r"indie\s*disco|silent\s*disco|kinderdisco|discozwemmen|feestfabriek|dutchtuber|dikkie\s*dik|"
                       r"ernst,?\s*bobbie|de\s*betovering|backstage\s*&\s*blik|open\s*mic|markt|bingo(?!\s+players)|subsidie\w*)\b"
                       r"|^opening:|\(\d{1,2}\+\)|pub\s*quiz|\bcomedy(?!\s+of\s+errors)\w*|\bfilmclub|science\s*&\s*cocktails", _re.I)
    for key in fresh:
        for e in fresh[key]:
            e["n"] = _re.sub(r"\s+", " ", e["n"]).strip()
            if ":" in (e.get("r") or ""): e["r"] = ""      # een label ('doors:') is geen zaalnaam
        drop = [e["n"] for e in fresh[key] if nonc.search(e["n"])]
        if drop:
            fresh[key] = [e for e in fresh[key] if not nonc.search(e["n"])]
            print(f"{key}: geen concert weggelaten: {sorted(set(drop))[:8]}")
        for e in fresh[key]:   # 00:00 en xx:59 zijn bij de zalen 'tijd onbekend' of nachtprogramma, geen aanvangstijd
            if e.get("t") == "00:00" or (e.get("t") or "").endswith(":59"): e["t"] = ""
    # zelfde concert bij twee zalen: de leidende zaal houdt het (BIRD/Rotown -> Rotown, De Helling/Tivoli -> Tivoli)
    tnorm = lambda t: _re.sub(r"[^a-z0-9]+", "", t.lower().split(" + ")[0].split(":")[0].split(" (")[0])
    for loser, leader in (("bird", "rotown"), ("annabel", "rotown"), ("helling", "tivoli")):
        if loser not in fresh: continue
        lead = fresh.get(leader) or [e for e in events.values() if e["v"] == leader]
        have = {}
        for e in lead: have.setdefault(e["d"], []).append(tnorm(e["n"]))
        def same(e):
            n = tnorm(e["n"])
            return any(n and o and (n in o or o in n) and min(len(n), len(o)) >= 4 for o in have.get(e["d"], []))
        before = len(fresh[loser])
        fresh[loser] = [e for e in fresh[loser] if not same(e)]
        if len(fresh[loser]) < before: print(f"{loser}: {before - len(fresh[loser])} dubbel met {leader} weggelaten")
    # Ticketmaster (officiële API) voor grote zalen en festivals; alleen als de sleutel als GitHub-secret bestaat
    tm_venues = store.get("venues", {})
    tm_key = os.environ.get("TM_API_KEY", "").strip()
    if not tm_key and not only:
        status["ticketmaster"] = {"ok": False, "error": "geen API-sleutel: zet TM_API_KEY als secret in GitHub", "at": None}
        print("ticketmaster: geen sleutel (TM_API_KEY) ingesteld")
    if tm_key and (not only or "ticketmaster" in only):
        try:
            raw = ticketmaster.fetch_all(tm_key)
            have = [e for g in fresh.values() for e in g] + [e for e in events.values() if not e["v"].startswith("tm-") and e["v"] not in fresh]
            got, info = ticketmaster.convert(raw, [e for e in have if e["d"] >= today])
            n = sum(len(g) for g in got.values())
            if n < 20:
                raise RuntimeError(f"only {n} events")
            for k in {v["v"] for v in events.values() if v["v"].startswith("tm-")} - set(got):
                got[k] = []   # locatie staat niet meer bij Ticketmaster: oude concerten opruimen
            fresh.update(got)
            tm_venues = {k: v for k, v in tm_venues.items() if k in got and got[k]}
            tm_venues.update(info)
            status["ticketmaster"] = {"ok": True, "count": n, "at": now, "venues": len(info)}
            print(f"ticketmaster: {n} concerten op {len(info)} locaties")
        except Exception as ex:
            status["ticketmaster"] = {"ok": False, "error": str(ex)[:200], "at": status.get("ticketmaster", {}).get("at"),
                                      "count": status.get("ticketmaster", {}).get("count")}
            print("ticketmaster: FAILED", ex)
    # eenmalig (2026-10-10): de uitbreiding met 28 zalen en de datumcorrecties zijn geen 'nieuwe' concerten
    if "baseline-2026-10-10" not in store.get("migrations", []):
        n0 = 0
        for e in events.values():
            if e.get("first") and e["first"] != "base" and e["first"] >= "2026-10-09":
                e["first"] = "base"; n0 += 1
        for g in fresh.values():
            for e in g: e["_base"] = True
        store.setdefault("migrations", []).append("baseline-2026-10-10")
        print("eenmalige basislijn:", n0, "concerten niet meer als nieuw")
    # merge: id = venue + date + url (stable); first_seen kept
    for key, got in fresh.items():
        ids = set()
        had = sum(1 for v in events.values() if v["v"] == key) >= 3
        for e in got:
            eid = f"{e['v']}|{e['d']}|{e['u']}"
            ids.add(eid)
            old = events.get(eid)
            # eerste keer dat een zaal binnenkomt: geen 'nieuw' (baseline)
            e["first"] = old["first"] if old else ("base" if e.pop("_base", False) or not had else today)
            e.pop("_base", None)
            e["last"] = today
            events[eid] = e
        # events of this venue no longer listed -> drop (cancelled/removed), unless past
        for eid in [k for k, v in events.items() if v["v"] == key and k not in ids]:
            del events[eid]
    if feed: feedimport.attach_ticketswap(events, feed)
    # directe TicketSwap-links uit de openbare sitemap van TicketSwap (gaat voor op de feed)
    try:
        n = tsmap.attach(events, tm_venues)
        status["ticketswap"] = {"ok": True, "count": n, "at": now}
        print("TicketSwap-links uit sitemap:", n)
    except Exception as ex:
        status["ticketswap"] = {"ok": False, "error": str(ex)[:200], "at": status.get("ticketswap", {}).get("at")}
        print("ticketswap sitemap: FAILED", ex)
    # keep past events one month for the archive
    cutoff = (date.today() - timedelta(days=45)).isoformat()
    for eid in [k for k, v in events.items() if v["d"] < cutoff]:
        del events[eid]
    store = {"events": events, "status": status, "updated": now, "venues": tm_venues, "migrations": store.get("migrations", [])}
    json.dump(store, open(os.path.join(DATA, "events.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    json.dump(pcache, open(os.path.join(DATA, "paradiso_cache.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    pub = sorted(events.values(), key=lambda e: (e["d"], e["v"], e["n"]))
    json.dump({"updated": now, "status": status, "venues": tm_venues, "events": pub}, open(os.path.join(OUT, "events.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("total", len(pub))

if __name__ == "__main__":
    main()
