#!/usr/bin/env python3
"""Haalt het Tivoli-programma op vanaf je eigen toestel (telefoon/pc) en zet het in de GitHub-repository.

Alleen standaardbibliotheek. Draait in Termux (Android) of op elke computer met Python 3.
Geeft Tivoli een bot-controle ("Just a moment..."), dan stopt het script. Het omzeilt niets.

Instellen:  export GITHUB_TOKEN=...   (fine-grained token, alleen deze repo, recht: Contents read/write)
Uitvoeren:  python3 tivoli_phone.py            (haalt op en uploadt)
            python3 tivoli_phone.py --dry-run  (haalt op, uploadt niet, schrijft tivoli_bundle.json)
"""
import base64, html, json, os, re, sys, time, urllib.request, urllib.error
from html.parser import HTMLParser

REPO = os.environ.get("TIVOLI_REPO", "bzwijgers/Concerten")
BASE = "https://www.tivolivredenburg.nl"
UA = "BarrysConcertAgenda/1.0 (persoonlijk gebruik; programma-overzicht)"
DELAY = 2.0
MAX_LIST_PAGES = 80
MAX_DETAIL = 120          # nieuwe concertpagina's per run

# genres die de gebruiker niet wil: klassiek, jazz, dance
EXCL = {"symfonisch", "kamermuziek", "oude-muziek", "strijkkwartet", "vocaal", "piano", "viool-altviool-cello",
        "blaasinstrumenten", "minimal-music", "filmmuziek", "nieuwe-muziek", "jazz",
        "classics-80s-90s-00s", "indie-pop-alternative", "hiphop-rb-soul", "global-1", "house-techno",
        "drum-n-bass-trap", "electronic"}

EV = re.compile(r"/agenda/(\d+)/([a-z0-9-]+?)-(\d\d)-(\d\d)-(\d{4})/?$")


class Blocked(Exception):
    pass


def get(url, token=None, raw=False):
    h = {"User-Agent": UA, "Accept-Language": "nl,en;q=0.8"}
    if token:
        h["Authorization"] = "Bearer " + token
        h["Accept"] = "application/vnd.github+json"
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            body = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace") if e.fp else ""
        if e.code in (403, 429) or "Just a moment" in body[:2000]:
            raise Blocked(f"HTTP {e.code} van {url}")
        raise
    if "<title>Just a moment" in body[:3000]:
        raise Blocked("bot-controle van Tivoli")
    return body


class Anchors(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.cur, self.txt = [], None, []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.cur, self.txt = dict(attrs).get("href", ""), []
    def handle_data(self, d):
        if self.cur is not None:
            self.txt.append(d)
    def handle_endtag(self, tag):
        if tag == "a" and self.cur is not None:
            self.out.append((self.cur, re.sub(r"\s+", " ", "".join(self.txt)).strip()))
            self.cur = None


def parse_list(page):
    """-> (events{id: {u,n,d}}, next_url or None)"""
    p = Anchors(); p.feed(page)
    evs, nxt = {}, None
    for href, text in p.out:
        path = re.sub(r"^https?://[^/]+", "", href.split("?")[0].split("#")[0])
        m = EV.search(path)
        if m:
            id_, slug, dd, mm, yy = m.groups()
            e = evs.setdefault(id_, {"u": BASE + path, "n": "", "d": f"{yy}-{mm}-{dd}", "slug": slug})
            if len(text) > len(e["n"]) and not text.lower().startswith(("add event", "remove event", "bestel", "gratis")):
                e["n"] = text
        elif "volgende evenementen" in text.lower() and href:
            nxt = href if href.startswith("http") else BASE + href
    for e in evs.values():
        if not e["n"]:
            e["n"] = e["slug"].replace("-", " ").title()
        e.pop("slug", None)
    return evs, nxt


def parse_detail(page):
    genres = sorted(set(re.findall(r"sf_genre=([a-z0-9-]+)", page)))
    if len(genres) > 5:      # waarschijnlijk het filtermenu van de site, niet de genres van dit concert
        genres = []
    rooms = sorted(set(re.findall(r"sf_venue_room=([a-z0-9-]+)", page)))
    text = re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<(script|style).*?</\1>", " ", page)).lower()
    return {"g": genres, "r": rooms, "s": "uitverkocht" in text}


def gh(path, token, method="GET", data=None):
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/{path}", method=method,
                                 data=json.dumps(data).encode() if data else None,
                                 headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
                                          "User-Agent": UA, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def main():
    dry = "--dry-run" in sys.argv
    token = os.environ.get("GITHUB_TOKEN") or ""
    if not token and not dry:
        sys.exit("Zet eerst GITHUB_TOKEN (zie stappenplan).")
    known = {}
    if token:
        try:
            st = gh("contents/data/manual/tivoli.json", token)
            known = json.loads(base64.b64decode(st["content"]).decode()).get("known", {})
        except Exception as ex:
            print("Kon bekende lijst niet laden:", ex)
    listed, url, seen_pages, sample_list = {}, BASE + "/agenda/", 0, None
    try:
        while url and seen_pages < MAX_LIST_PAGES:
            page = get(url)
            if sample_list is None:
                sample_list = page[:150000]
            evs, nxt = parse_list(page)
            new = [i for i in evs if i not in listed]
            listed.update(evs)
            seen_pages += 1
            print(f"pagina {seen_pages}: {len(evs)} concerten ({len(new)} nieuw)")
            if not new:
                break
            if not nxt:
                nxt = f"{BASE}/agenda/page/{seen_pages + 1}/"
            url = nxt
            time.sleep(DELAY)
        details, todo = {}, [i for i in listed if i not in known][:MAX_DETAIL]
        sample_detail = None
        for n, i in enumerate(todo, 1):
            page = get(listed[i]["u"])
            if sample_detail is None:
                sample_detail = page[:150000]
            d = parse_detail(page)
            d["x"] = bool(set(d["g"]) & EXCL)
            details[i] = d
            print(f"  detail {n}/{len(todo)} {listed[i]['n']}: {','.join(d['g']) or '?'}{' (weg)' if d['x'] else ''}")
            time.sleep(DELAY)
    except Blocked as ex:
        sys.exit(f"Gestopt: {ex}. Tivoli laat dit apparaat nu niet door; er is niets geüpload.")
    complete = seen_pages >= 2 and len(listed) >= 100
    bundle = {"fetched": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "complete": complete,
              "listed": [dict(id=i, **e) for i, e in sorted(listed.items(), key=lambda kv: kv[1]["d"])],
              "details": details, "samples": {"list": sample_list, "detail": sample_detail} if len(known) == 0 or not complete else {}}
    print(f"Totaal {len(listed)} concerten, {len(details)} nieuwe pagina's gelezen, volledig={complete}")
    if dry:
        json.dump(bundle, open("tivoli_bundle.json", "w", encoding="utf-8"), ensure_ascii=False)
        print("tivoli_bundle.json geschreven (niet geüpload)")
        return
    if len(listed) < 20:
        sys.exit("Te weinig concerten gevonden; niet geüpload.")
    path = "contents/data/inbox/tivoli.json"
    sha = None
    try:
        sha = gh(path, token)["sha"]
    except urllib.error.HTTPError:
        pass
    body = {"message": "Tivoli-programma van telefoon", "content": base64.b64encode(json.dumps(bundle, ensure_ascii=False).encode()).decode()}
    if sha:
        body["sha"] = sha
    gh(path, token, "PUT", body)
    print("Geüpload. De agenda wordt bij de eerstvolgende update (of nu meteen) bijgewerkt.")


if __name__ == "__main__":
    main()
