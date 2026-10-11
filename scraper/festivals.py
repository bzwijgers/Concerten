"""Festivals: de data van de volgende editie, van de eigen site van het festival (schema.org of de tekst op de
voorpagina, zoals '18 • 19 • 20 juni 2027' of '2 t/m 4 juli 2027'). Staan de nieuwe data er nog niet, dan
komt het festival (nog) niet in de agenda; dat is geen fout. Eén regel per festival, op de eerste dag, met de
laatste dag in 'e'. Concerten van Ticketmaster met de naam van het festival in die dagen vallen weg (geen dubbele)."""
import re
from datetime import date
from common import fetch, ld_events, ev

# key: (naam, plaats, land, site)
FEST = {
    "fest_bospop": ("Bospop", "Weert", "NL", "https://www.bospop.nl/"),
    "fest_pinkpop": ("Pinkpop", "Landgraaf", "NL", "https://www.pinkpop.nl/"),
    "fest_lowlands": ("Lowlands", "Biddinghuizen", "NL", "https://lowlands.nl/"),
    "fest_dtrh": ("Down the Rabbit Hole", "Beuningen", "NL", "https://downtherabbithole.nl/"),
    "fest_bks": ("Best Kept Secret", "Hilvarenbeek", "NL", "https://www.bestkeptsecret.nl/"),
    "fest_baroeg": ("Baroeg Open Air", "Rotterdam", "NL", "https://www.baroegopenair.nl/"),
    "fest_dynamo": ("Dynamo Metalfest", "Eindhoven", "NL", "https://dynamo-metalfest.nl/"),
    "fest_itg": ("Into The Grave", "Leeuwarden", "NL", "https://www.intothegrave.nl/"),
    "fest_lotd": ("Left of the Dial", "Rotterdam", "NL", "https://www.leftofthedial.nl/"),
    "fest_werchter": ("Rock Werchter", "Werchter", "BE", "https://www.rockwerchter.be/"),
    "fest_graspop": ("Graspop Metal Meeting", "Dessel", "BE", "https://www.graspop.be/nl/"),
    "fest_alcatraz": ("Alcatraz", "Kortrijk", "BE", "https://www.alcatraz.be/nl/"),
}

MONTHS = {"jan": 1, "feb": 2, "mrt": 3, "maa": 3, "mar": 3, "apr": 4, "mei": 5, "may": 5, "jun": 6, "jul": 7, "aug": 8,
          "sep": 9, "okt": 10, "oct": 10, "nov": 11, "dec": 12}
RANGE = re.compile(r"\b(\d{1,2})((?:\s*(?:[-–•,./&+]|t/m|tot en met|tot|en|and)\s*\d{1,2}){0,5})\.?\s+"
                   r"(januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december|"
                   r"january|february|march|may|june|july|august|october|"
                   r"jan|feb|mrt|mar|apr|jun|jul|aug|sep|sept|okt|oct|nov|dec)\.?,?\s+(20\d\d)\b", re.I)


def _text(page):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", page, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t.replace("&amp;", "&").replace("&#8211;", "–").replace("&nbsp;", " "))


def dates(page):
    """[(eerste dag, laatste dag)] van de toekomstige edities die op de pagina staan, meest genoemde eerst."""
    today = date.today().isoformat()
    found = {}
    for o in ld_events(page):
        a, b = str(o.get("startDate", ""))[:10], str(o.get("endDate", "") or o.get("startDate", ""))[:10]
        if re.match(r"\d{4}-\d\d-\d\d$", a) and b >= today:
            found[(a, b)] = found.get((a, b), 0) + 5
    txt = _text(page)
    if not RANGE.search(txt): txt = re.sub(r"<[^>]+>|\u003c[^>]*?\u003e", " ", page)   # sommige sites zetten de tekst in een script
    for m in RANGE.finditer(txt):
        days = [int(m.group(1))] + [int(x) for x in re.findall(r"\d{1,2}", m.group(2))]
        mo, y = MONTHS.get(m.group(3).lower()[:3]), int(m.group(4))
        if not mo or len(days) < 2 or days != sorted(days) or days[-1] - days[0] > 5: continue   # een festival duurt een paar dagen
        try:
            a, b = date(y, mo, days[0]).isoformat(), date(y, mo, days[-1]).isoformat()
        except ValueError:
            continue
        if b >= today: found[(a, b)] = found.get((a, b), 0) + 1
    return sorted(found, key=lambda k: (-found[k], k))


def make(key):
    name, city, cc, url = FEST[key]
    def run():
        ds = dates(fetch(url, tries=2, timeout=30))
        if not ds: return []
        a, b = ds[0]
        e = ev(key, a, f"{name} {a[:4]}", url)
        e["e"] = b
        return [e]
    return run


def drop_tm_duplicates(tm, fests):
    """tm: dict zaal -> concerten van Ticketmaster; fests: festivalregels. Weg met kaartjes voor die festivals in die dagen."""
    def norm(s): return re.sub(r"[^a-z0-9]", "", s.lower())
    rules = [(norm(FEST[f["v"]][0]), f["d"], f.get("e", f["d"])) for f in fests]
    n = 0
    for k in tm:
        keep = []
        for x in tm[k]:
            if any(nm in norm(x["n"]) and a <= x["d"] <= b for nm, a, b in rules): n += 1; continue
            keep.append(x)
        tm[k] = keep
    if n: print(f"ticketmaster: {n} festivalkaartjes weggelaten (festival staat er zelf in)")
