"""Afbeelding per concert (voor de foto in de lijst): de og:image van de eigen concertpagina van de zaal.
Elke pagina wordt hooguit één keer gelezen; de uitkomst staat in data/images.json. Per zaal per run een beperkt aantal,
zodat de sites niet zwaar belast worden: na een paar dagen is alles gevuld."""
import html as _html, json, os, re, time
from concurrent.futures import ThreadPoolExecutor
from common import fetch

PER_VENUE = 60
SKIP = {"tivoli", "o13", "bolwerk", "sounddog", "amare"}   # GitHub wordt daar soms geweigerd / geen concertpagina


def og_image(page):
    for pat in (r'<meta[^>]+property=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)',
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
                r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)'):
        m = re.search(pat, page, re.I)
        if m:
            u = _html.unescape(m.group(1)).strip()
            if u.startswith("//"): u = "https:" + u
            if u.startswith("http") and not re.search(r"logo|favicon|placeholder|default[-_]?(share|og)", u, re.I):
                return u
    return ""


def fill(events, data_dir):
    """events: dict id -> event (alle bekende concerten). Zet e['img'] waar een afbeelding bekend is."""
    from datetime import date
    path = os.path.join(data_dir, "images.json")
    try:
        cache = json.load(open(path, encoding="utf-8"))
    except Exception:
        cache = {}
    today = date.today().isoformat()
    todo = {}
    for e in events.values():
        if e["d"] < today or e["v"].startswith("tm-") or e["v"] in SKIP: continue
        if e.get("img"): cache.setdefault(e["u"], e["img"]); continue
        if e["u"] in cache or not e["u"].startswith("http") or "stager.co" in e["u"]: continue
        todo.setdefault(e["v"], []).append(e["u"])

    def work(item):
        v, urls = item
        n = 0
        for u in urls[:PER_VENUE]:
            try:
                cache[u] = og_image(fetch(u, tries=1, timeout=25))
            except Exception:
                cache[u] = ""
            n += 1
            time.sleep(1)
        return n

    with ThreadPoolExecutor(6) as ex:
        total = sum(ex.map(work, todo.items()))
    for e in events.values():
        if not e.get("img") and cache.get(e["u"]): e["img"] = cache[e["u"]]
    live = {e["u"] for e in events.values()}
    json.dump({u: i for u, i in cache.items() if u in live}, open(path, "w", encoding="utf-8"), separators=(",", ":"))
    print(f"afbeeldingen: {total} pagina's gelezen, {sum(1 for e in events.values() if e.get('img') and e['d'] >= today)} concerten met foto")


def thumbs(events, docs_dir, data_dir, limit=800):
    """Kleine miniaturen (112x112 webp, ~4 kB) in docs/thumbs/, zodat de app niet de grote foto's van de zalen laadt."""
    import hashlib, io, urllib.request
    from datetime import date
    try:
        from PIL import Image
    except ImportError:
        print("miniaturen: Pillow ontbreekt"); return
    tdir = os.path.join(docs_dir, "thumbs"); os.makedirs(tdir, exist_ok=True)
    path = os.path.join(data_dir, "thumbs.json")
    try:
        done = json.load(open(path, encoding="utf-8"))     # afbeelding-url -> bestandsnaam ('' = mislukt)
    except Exception:
        done = {}
    today = date.today().isoformat()
    want = {e["img"] for e in events.values() if e.get("img") and e["d"] >= today}
    todo = [u for u in want if u not in done][:limit]

    def one(u):
        name = hashlib.sha1(u.encode()).hexdigest()[:16] + ".webp"
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "BarrysConcertAgenda/1.0 (+https://github.com/bzwijgers/Concerten)"})
            with urllib.request.urlopen(req, timeout=25) as r:
                im = Image.open(io.BytesIO(r.read())).convert("RGB")
            w, h = im.size; s = min(w, h)
            im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((112, 112), Image.LANCZOS)
            im.save(os.path.join(tdir, name), "WEBP", quality=62, method=6)
            return u, name
        except Exception:
            return u, ""

    with ThreadPoolExecutor(8) as ex:
        for u, name in ex.map(one, todo):
            done[u] = name
    for e in events.values():
        n = done.get(e.get("img") or "")
        if n: e["th"] = "thumbs/" + n
    keep = {done[u] for u in want if done.get(u)}
    for f in os.listdir(tdir):                              # miniaturen van voorbije concerten opruimen
        if f.endswith(".webp") and f not in keep:
            os.remove(os.path.join(tdir, f))
    json.dump({u: n for u, n in done.items() if u in want}, open(path, "w", encoding="utf-8"), separators=(",", ":"))
    print(f"miniaturen: {len(todo)} nieuw, {len(keep)} in gebruik")
