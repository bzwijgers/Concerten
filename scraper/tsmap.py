"""Directe TicketSwap-links via de openbare sitemap van TicketSwap (robots.txt staat die toe).
Elke evenementpagina heeft een adres als
  https://www.ticketswap.com/concert-tickets/<artiest>-<stad>-<zaal>-<yyyy-mm-dd>-<id>
Daarmee koppelen we een concert op datum + artiest (+ zaal als er meerdere kandidaten zijn)."""
import gzip, re, time, urllib.request

UA = "BarrysConcertAgenda/1.0 (+https://github.com/bzwijgers/Concerten)"
INDEX = "https://www.ticketswap.com/sitemap.xml"
LOC = re.compile(r"<loc>(https://www\.ticketswap\.com/[a-z-]+-tickets/([a-z0-9-]+?)-(\d{4}-\d\d-\d\d)-[A-Za-z0-9]+)</loc>")

# hoe de zaal in TicketSwap-adressen heet (genormaliseerd, zonder streepjes)
VENUE_HINT = {"paradiso": "paradiso", "melkweg": "melkweg", "tivoli": "tivolivredenburg", "o13": "013", "paard": "paard",
              "mezz": "mezz", "effenaar": "effenaar", "pul": "pul", "boerderij": "boerderij", "patronaat": "patronaat",
              "hedon": "hedon", "helling": "helling", "dynamo": "dynamo", "klokgebouw": "klokgebouw", "doornroosje": "doornroosje",
              "metropool": "metropool", "spot": "oosterpoort", "bibelot": "bibelot", "bosuil": "bosuil", "bird": "bird",
              "gebouwt": "gebouwt", "neushoorn": "neushoorn", "amare": "amare", "tolhuistuin": "tolhuistuin", "rotown": "rotown",
              "baroeg": "baroeg", "dbs": "dbs", "bolwerk": "bolwerk",
              "burgerweeshuis": "burgerweeshuis", "ekko": "ekko", "nobel": "nobel", "grenswerk": "grenswerk", "iduna": "iduna", "musicon": "musicon",
              "qfactory": "qfactory", "simplon": "simplon", "sounddog": "sounddog", "vera": "vera", "victorie": "victorie"}


CITY = {"paradiso": "amsterdam", "melkweg": "amsterdam", "tolhuistuin": "amsterdam", "tivoli": "utrecht", "helling": "utrecht",
        "dbs": "utrecht", "o13": "tilburg", "paard": "denhaag", "amare": "denhaag", "mezz": "breda", "effenaar": "eindhoven",
        "dynamo": "eindhoven", "klokgebouw": "eindhoven", "pul": "uden", "boerderij": "zoetermeer", "patronaat": "haarlem",
        "hedon": "zwolle", "doornroosje": "nijmegen", "metropool": "", "spot": "groningen", "bibelot": "dordrecht",
        "bosuil": "weert", "bird": "rotterdam", "rotown": "rotterdam", "baroeg": "rotterdam", "gebouwt": "bergenopzoom",
        "neushoorn": "leeuwarden", "bolwerk": "sneek",
        "burgerweeshuis": "deventer", "ekko": "utrecht", "nobel": "leiden", "grenswerk": "venlo", "iduna": "drachten", "musicon": "denhaag", "qfactory": "amsterdam", "simplon": "groningen", "sounddog": "breda", "vera": "groningen", "victorie": "alkmaar"}
ART = re.compile(r"<loc>(https://www\.ticketswap\.com/artist/([a-z0-9-]+)-tickets-[A-Za-z0-9]+)</loc>")


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        raw = r.read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", "replace")


def load_index(first_date):
    """{datum: [(genormaliseerde slug, url)]} voor alle evenementen vanaf first_date."""
    maps = [m for m in re.findall(r"<loc>([^<]+)</loc>", _get(INDEX)) if "/event_" in m or "/alias_event_" in m or "/artist_" in m]
    by_day, n = {"artists": {}}, 0
    for u in maps:
        for _ in range(2):
            try:
                x = _get(u); break
            except Exception as ex:
                x = ""; print("ticketswap sitemap mislukt:", u, type(ex).__name__); time.sleep(3)
        for url, slug in ART.findall(x):
            by_day["artists"].setdefault(norm(slug), url.replace("https://www.ticketswap.com/", "https://www.ticketswap.nl/"))
        for url, slug, d in LOC.findall(x):
            if d >= first_date:
                by_day.setdefault(d, []).append((norm(slug), url)); n += 1
        time.sleep(0.5)
    print(f"ticketswap sitemap: {len(maps)} bestanden, {n} evenementen vanaf {first_date}")
    return by_day


def match(e, by_day, label=""):
    cands = by_day.get(e["d"])
    if not cands: return None
    title = e["n"].lower()
    first = re.split(r"\s+(?:\+|&|x|w/|ft\.?|feat\.?|presents:?|-|–|\|)\s+|:\s|\s\(", title)[0]
    a = norm(first)
    if len(a) < 3: return None
    hits = [(s, u) for s, u in cands if a in s]
    if not hits: return None
    hint = VENUE_HINT.get(e["v"]) or norm(label)
    if hint:
        best = [h for h in hits if hint in h[0]]
        city = CITY.get(e["v"]) or norm(e.get("r") or "")
        if best: hits = best
        elif city and len(hits) == 1 and city in hits[0][0]: pass   # zaal anders gespeld, stad klopt
        else: return None
    if len(hits) > 1:   # meerdere: kies de kortste slug (minst extra tekst), maar alleen bij één duidelijke
        hits.sort(key=lambda h: len(h[0]))
        if len(hits[0][0]) == len(hits[1][0]): return None
    return hits[0][1].replace("https://www.ticketswap.com/", "https://www.ticketswap.nl/")


def attach(events, venues=None):
    """Zet e['k'] (directe TicketSwap-link) bij toekomstige concerten. Geeft het aantal koppelingen."""
    from datetime import date
    today = date.today().isoformat()
    by_day = load_index(today)
    if not by_day:
        raise RuntimeError("lege sitemap")
    n = 0
    for e in events.values():
        if e["d"] < today: continue
        k = match(e, by_day, ((venues or {}).get(e["v"]) or {}).get("label", ""))
        if k:
            e["k"] = k; n += 1
            e.pop("ka", None)
        else:   # geen evenementpagina: dan de artiestpagina op TicketSwap (alleen bij exact dezelfde naam)
            first = re.split(r"\s+(?:\+|&|x|w/|ft\.?|feat\.?|-|–|\|)\s+|:\s|\s\(", e["n"].lower())[0]
            a = by_day["artists"].get(norm(first))
            if a and len(norm(first)) >= 3: e["ka"] = a
    return n
