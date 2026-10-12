"""Het Concertgebouw (Amsterdam): alleen concerten met het genre 'Pop' (of een pop-label).
Hun overzicht bladert via adressen die robots.txt verbiedt, dus: de sitemap van concertpagina's, nieuwste eerst,
per run hooguit PER_RUN nieuwe pagina's lezen en de uitkomst onthouden in data/concertgebouw.json.
De pagina's zijn Nuxt-pagina's: genre-namen staan als verwijzing (title:bH) naar de argumenten van het
__NUXT__-script; die vertalen we terug."""
import json, os, re, time
from datetime import date
from common import fetch, ld_events, ev, sold_from_offers

PER_RUN = 80
PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "concertgebouw.json")
POP = re.compile(r"^(pop|rock|singer-songwriter|indie|soul|r&b|hiphop|hip-hop|blues|americana|folk|country|pop-)", re.I)


def _args(src):
    """Splits de argumentenlijst van het __NUXT__-script in losse waarden (strings, getallen, null, ...)."""
    out, i, n, depth, cur, q = [], 0, len(src), 0, "", None
    while i < n:
        c = src[i]
        if q:
            cur += c
            if c == "\\": cur += src[i + 1]; i += 1
            elif c == q: q = None
        elif c in "\"'":
            q = c; cur += c
        elif c in "([{":
            depth += 1; cur += c
        elif c in ")]}":
            depth -= 1; cur += c
        elif c == "," and depth == 0:
            out.append(cur.strip()); cur = ""
        else:
            cur += c
        i += 1
    if cur.strip(): out.append(cur.strip())
    return out


def _vars(page):
    m = re.search(r"__NUXT__=\(function\(([^)]*)\)\{", page)
    if not m: return {}
    names = m.group(1).split(",")
    end = page.rfind("}(", m.end())
    tail = page[end + 2:]
    tail = tail[:tail.find("));")] if "));" in tail else tail
    vals = _args(tail)
    out = {}
    for k, v in zip(names, vals):
        if v.startswith('"'):
            try: out[k] = json.loads(v)
            except Exception: out[k] = v.strip('"')
    return out


def _genres(page):
    vs = _vars(page)
    titles = []
    for block in re.findall(r"genres:\[([^\]]*)\]", page)[:2] + re.findall(r"tags:\[([^\]]*)\]", page)[:2]:
        for t in re.findall(r'title:("[^"]*"|[A-Za-z_$][\w$]*)', block):
            titles.append(json.loads(t) if t.startswith('"') else vs.get(t, ""))
    return [t for t in titles if t]


def concertgebouw():
    try: cache = json.load(open(PATH, encoding="utf-8"))
    except Exception: cache = {}
    rows = []
    for n in range(12):
        try: sm = fetch(f"https://www.concertgebouw.nl/sitemap_sections_6_{n}.xml", tries=1)
        except Exception: break
        rows += re.findall(r"<loc>([^<]+/concerten/[^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", sm)
    if not rows: raise RuntimeError("geen concertpagina's in de sitemap")
    rows.sort(key=lambda r: r[1], reverse=True)
    today, done = date.today().isoformat(), 0
    for u, lm in rows:
        c = cache.get(u)
        if c and (c.get("lm") == lm or c.get("d", "9") < today): continue
        if done >= PER_RUN: break
        done += 1
        try:
            p = fetch(u, tries=1, timeout=40)
        except Exception:
            continue
        ld = [o for o in ld_events(p) if o.get("startDate")]
        gs = _genres(p)
        cache[u] = {"lm": lm, "g": gs[:6], "ev": [[str(o["startDate"])[:10], str(o["startDate"])[11:16], o.get("name", ""), sold_from_offers(o)] for o in ld][:10],
                    "d": max([str(o["startDate"])[:10] for o in ld] or ["0"])}
        time.sleep(0.8)
    live = {u for u, _ in rows}
    cache = {u: (c if c.get("d", "0") >= today else {"lm": c.get("lm"), "d": c.get("d", "0")}) for u, c in cache.items() if u in live}   # voorbij: alleen onthouden dat we hem kennen
    json.dump(cache, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    out = []
    for u, c in cache.items():
        if not any(POP.search(g) for g in c.get("g", [])): continue
        if any(re.search(r"klassiek|classical", g + " ", re.I) for g in c.get("g", [])) and not any(re.match(r"pop", g, re.I) for g in c.get("g", [])): continue
        for d, t, n, s in c["ev"]:
            if d >= today and not re.search(r"classical|klassiek", n, re.I): out.append(ev("concertgebouw", d, n, u, t, "", s))
    print(f"concertgebouw: {done} pagina's gelezen, {len(cache)} komende concerten bekend, {len(out)} pop")
    return out
