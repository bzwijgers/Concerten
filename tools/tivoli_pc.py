#!/usr/bin/env python3
"""Tivoli-programma ophalen op de eigen pc van de eigenaar en via git in de repository zetten.

Tivoli laat de servers van GitHub niet door, maar wel een gewone thuisverbinding. Dit script leest de
agenda van tivolivredenburg.nl (zoals een bezoeker), zet het resultaat in data/inbox/tivoli.json en pusht
dat met de git-inlog die al op de pc staat. Bij een bot-controle stopt het: er wordt niets omzeild.

Gebruik:  python tivoli_pc.py [pad-naar-repo]        (standaard: de repo waar dit script in staat)
          python tivoli_pc.py --dry-run               (niets committen)
Alleen standaardbibliotheek.
"""
import html, json, os, re, subprocess, sys, time, urllib.request, urllib.error
from datetime import date

BASE = "https://www.tivolivredenburg.nl"
UA = "BarrysConcertAgenda/1.0 (persoonlijk gebruik; programma-overzicht)"
DELAY = 1.5
MAX_PAGES = 80
MAX_DETAIL = 600   # tijden van nieuwe concerten per run (alleen nieuwe; bekende tijden worden onthouden)

# alleen popgenres (genrelijst van Tivoli zelf); geen klassiek, jazz, dance, talks of comedy
GOOD = {"pop", "rock", "pop-rock", "indie", "singer-songwriter", "roots-blues-americana", "metal-punk-heavy",
        "metal", "punk", "hiphop-rb-1", "hiphop-rb-soul", "classic-pop-60s-90s", "nederlands", "global-1-pop-rock",
        "reggae-ska", "indie-pop-alternative"}
BAD = {"klassiek", "kamermuziek", "symfonisch", "oude-muziek", "strijkkwartet", "vocaal", "piano", "orgel",
       "viool-altviool-cello", "blaasinstrumenten", "minimal-music", "filmmuziek", "nieuwe-muziek", "hedendaags",
       "jazz", "soul-funk-jazz", "dance-by-night", "house-techno", "electronic", "electronic-1", "drum-n-bass-trap",
       "familie", "talk", "film", "literatuur"}
NOT_MUSIC = re.compile(r"\b(yoga|boekenclub|masterclass|podcast|lezing|rondleiding|workshop|college|quiz|"
                       r"orgelwoensdag|zanggroepen|kinder\w*|familieconcert)\b", re.I)


class Blocked(Exception):
    pass


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "nl,en;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            body = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            raise Blocked(f"HTTP {e.code}")
        raise
    if "Just a moment" in body[:3000] or "cf-challenge" in body[:5000]:
        raise Blocked("bot-controle")
    return body


def txt(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def parse_list(page):
    out = []
    for li in re.findall(r'<li class="agenda-list-item[^"]*">(.*?)</li>', page, re.S):
        a = re.search(r'agenda-list-item__title-link[^>]*href="([^"]+)"[^>]*>(.*?)</a>', li, re.S)
        if not a: continue
        u = a.group(1).split("?")[0].rstrip("/")
        m = re.search(r"/agenda/(\d+)/[a-z0-9-]+?-(\d{1,2})-(\d{1,2})-(\d{4})$", u)
        if not m: continue
        genres = [g.strip() for g in (re.search(r'data-genre="([^"]*)"', li) or [None, ""])[1].split(",") if g.strip()]
        sub = txt((re.search(r'agenda-list-item__text">(.*?)</p>', li, re.S) or [None, ""])[1])
        room = sub.split("| in ", 1)[1].strip() if "| in " in sub else ""
        out.append({"id": m.group(1), "u": u, "n": txt(a.group(2)), "d": f"{m.group(4)}-{int(m.group(3)):02d}-{int(m.group(2)):02d}",
                    "g": genres, "r": room, "s": "agenda-list-item__label\">Uitverkocht" in li})
    nxt = re.search(r'href="([^"]+/agenda/page/\d+/)"', page)
    return out, nxt.group(1) if nxt else None


def detail_time(page):
    t = txt(re.sub(r"(?s)<(script|style).*?</\1>", " ", page))
    m = re.search(r"(\d{1,2}[:.]\d{2})\s*Aanvang", t) or re.search(r"Aanvang\s*:?\s*(\d{1,2}[:.]\d{2})", t)
    if m:
        return m.group(1).replace(".", ":").zfill(5)
    m = re.search(r'"startDate":"\d{4}-\d\d-\d\dT(\d\d:\d\d)', page)
    return m.group(1) if m else ""


def o13_events():
    """Reserve voor 013: GitHub krijgt daar soms een bot-controle, deze pc niet. Zelfde gegevens als de lijstpagina."""
    try:
        h = get("https://www.013.nl/programma")
    except Exception as ex:
        print("013 niet gelukt:", ex); return []
    out = []
    for art in re.findall(r"<article\b.*?</article>", h, re.S):
        a = re.search(r'href="(https://www\.013\.nl/programma/[^"]+)"', art)
        t = re.search(r"<h2[^>]*>(.*?)</h2>", art, re.S)
        tm = re.search(r'<time[^>]*datetime="(\d{4}-\d\d-\d\d)T(\d\d:\d\d)', art)
        if a and t and tm:
            out.append({"v": "o13", "d": tm.group(1), "n": txt(t.group(1)), "u": a.group(1), "t": tm.group(2), "r": "",
                        "s": "uitverkocht" in art.lower(), "c": False})
    print(f"013: {len(out)} concerten (reserve)")
    return out


def keep(e):
    if NOT_MUSIC.search(e["n"]): return False
    return any(g in GOOD for g in e["g"])


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)


def sync(repo):
    """Deze kopie is alleen voor dit script: altijd precies gelijk aan GitHub zetten (geen merge-conflicten)."""
    git(repo, "rebase", "--abort"); git(repo, "merge", "--abort")
    git(repo, "fetch", "-q", "origin")
    git(repo, "checkout", "-q", "-f", "main")
    r = git(repo, "reset", "-q", "--hard", "origin/main")
    if r.returncode: print("git reset mislukt:", r.stderr.strip())


def main():
    dry = "--dry-run" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    repo = os.path.abspath(args[0] if args else os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    if not dry:
        sync(repo)
    try:
        times = json.load(open(os.path.join(repo, "data", "manual", "tivoli.json"), encoding="utf-8")).get("times", {})
    except Exception:
        times = {}
    listed, url, pages = {}, BASE + "/agenda/", 0
    try:
        while url and pages < MAX_PAGES:
            try:
                page = get(url)
            except urllib.error.HTTPError as ex:
                if ex.code == 404 and pages: break      # voorbij de laatste pagina
                raise
            evs, nxt = parse_list(page)
            new = [e for e in evs if e["id"] not in listed]
            for e in evs: listed.setdefault(e["id"], e)
            pages += 1
            print(f"pagina {pages}: {len(evs)} items ({len(new)} nieuw)")
            if not new or not nxt: break
            url = f"{BASE}/agenda/page/{pages + 1}/"
            time.sleep(DELAY)
        events = [e for e in listed.values() if keep(e) and e["d"] >= date.today().isoformat()]
        todo = [e for e in events if e["id"] not in times][:MAX_DETAIL]
        for n, e in enumerate(todo, 1):
            time.sleep(DELAY)
            try:
                times[e["id"]] = detail_time(get(e["u"]))
            except Blocked:
                raise
            except Exception as ex:
                print("  detail mislukt:", e["u"], ex)
            if n % 25 == 0: print(f"  tijden {n}/{len(todo)}")
    except Blocked as ex:
        sys.exit(f"Gestopt: {ex}. Tivoli laat deze verbinding nu niet door; er is niets veranderd.")
    complete = pages >= 2 and len(listed) >= 100
    out = [{"v": "tivoli", "d": e["d"], "n": e["n"], "u": e["u"], "t": times.get(e["id"], ""), "r": e["r"],
            "s": e["s"], "c": False, "g": e["g"]} for e in sorted(events, key=lambda e: (e["d"], e["n"]))]
    print(f"{len(listed)} items op de site, {len(out)} concerten na filter, {len(todo)} tijden opgehaald, volledig={complete}")
    if len(out) < 20:
        sys.exit("Te weinig concerten gevonden; niets gedaan.")
    bundle = {"format": 2, "fetched": time.strftime("%Y-%m-%dT%H:%M:%S"), "complete": complete, "events": out,
              "times": {i: t for i, t in times.items() if i in listed}}
    p = os.path.join(repo, "data", "inbox", "tivoli.json")
    o13 = o13_events()
    p13 = os.path.join(repo, "data", "inbox", "o13.json")

    def write():
        os.makedirs(os.path.dirname(p), exist_ok=True)
        json.dump(bundle, open(p, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        if len(o13) >= 20:
            json.dump({"format": 2, "fetched": bundle["fetched"], "events": o13}, open(p13, "w", encoding="utf-8"),
                      ensure_ascii=False, separators=(",", ":"))
    if dry:
        write(); print("geschreven naar", p, "(niet gecommit)")
        return
    for attempt in range(4):
        sync(repo); write()          # telkens op de nieuwste stand van GitHub, dan pas ons bestand erbij
        git(repo, "add", "data/inbox/tivoli.json", "data/inbox/o13.json")
        git(repo, "-c", "user.name=Barry (pc)", "-c", "user.email=bot@users.noreply.github.com",
            "commit", "-q", "-m", f"Tivoli-programma van eigen pc ({len(out)} concerten)")
        r = git(repo, "push", "-q", "origin", "main")
        if not r.returncode:
            print("Gepusht; GitHub verwerkt het meteen."); return
        print("push geweigerd, opnieuw:", r.stderr.strip()[:200])
        time.sleep(20 * (attempt + 1))
    sys.exit("push mislukt: " + r.stderr.strip())


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        import traceback; traceback.print_exc(); sys.exit(1)
