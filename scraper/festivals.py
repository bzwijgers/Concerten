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
    "fest_zeeltje": ("Zeeltje", "Deest", "NL", "https://www.festivalzeeltje.nl/nieuws.php"),
    "fest_paaspop": ("Paaspop", "Schijndel", "NL", "https://www.paaspop.nl/"),
    "fest_zwartecross": ("Zwarte Cross", "Lichtenvoorde", "NL", "https://zwartecross.nl/"),
    "fest_esns": ("Eurosonic Noorderslag", "Groningen", "NL", "https://esns.nl/"),
    "fest_motel": ("Motel Mozaïque", "Rotterdam", "NL", "https://www.motelmozaique.nl/"),
    "fest_lgw": ("Le Guess Who?", "Utrecht", "NL", "https://leguesswho.nl/"),
    "fest_cb": ("Crossing Border", "Den Haag", "NL", "https://crossingborder.nl/"),
    "fest_itgwo": ("Into The Great Wide Open", "Vlieland", "NL", "https://www.intothegreatwideopen.nl/"),
    "fest_roadburn": ("Roadburn", "Tilburg", "NL", "https://roadburn.com/"),
    "fest_jera": ("Jera On Air", "Ysselsteyn", "NL", "https://www.jeraonair.nl/"),
    "fest_soh": ("South of Heaven", "Maastricht", "NL", "https://southofheaven.nl/"),
    "fest_pitfest": ("Pitfest", "Emmen", "NL", "https://pitfest.nl/"),
    "fest_waterpop": ("Waterpop", "Wateringen", "NL", "https://www.waterpop.nl/"),
    "fest_groezrock": ("Groezrock", "Meerhout", "BE", "https://www.groezrock.be/"),
    "fest_pukkelpop": ("Pukkelpop", "Hasselt", "BE", "https://www.pukkelpop.be/"),
    "fest_lokerse": ("Lokerse Feesten", "Lokeren", "BE", "https://www.lokersefeesten.be/"),
    "fest_suikerrock": ("Suikerrock", "Tienen", "BE", "https://www.suikerrock.be/"),
    "fest_zottegem": ("Rock Zottegem", "Zottegem", "BE", "http://www.rockzottegem.be/"),
    "fest_dour": ("Dour Festival", "Dour", "BE", "https://www.dourfestival.eu/"),
    "fest_twclassic": ("TW Classic", "Werchter", "BE", "https://www.twclassic.be/"),
    "fest_werchter": ("Rock Werchter", "Werchter", "BE", "https://www.rockwerchter.be/"),
    "fest_graspop": ("Graspop Metal Meeting", "Dessel", "BE", "https://www.graspop.be/nl/"),
    "fest_alcatraz": ("Alcatraz", "Kortrijk", "BE", "https://www.alcatraz.be/nl/"),
}

MONTHS = {"jan": 1, "feb": 2, "mrt": 3, "maa": 3, "mar": 3, "apr": 4, "mei": 5, "may": 5, "jun": 6, "jul": 7, "aug": 8,
          "sep": 9, "okt": 10, "oct": 10, "nov": 11, "dec": 12}
MON = (r"januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december|"
       r"january|february|march|may|june|july|august|october|jan|feb|mrt|mar|apr|jun|jul|aug|sept|sep|okt|oct|nov|dec")
DAYS = r"\d{1,2}(?:\s*(?:[-–—•,./&+]|t/m|tot en met|tot|en|and)\s*\d{1,2}){1,9}"
# '18 • 19 • 20 juni 2027', '13 — 16 jan 2027', '26-27-28 maart' (jaar elders)
RANGE = re.compile(r"\b(" + DAYS + r")\.?\s+(" + MON + r")\b\.?,?(?:\s+(20\d\d)\b)?", re.I)
# 'April 15-18, 2027', 'June 24-25-26', '07+08+09+10+11 July' wordt hierboven al gevonden
RANGE2 = re.compile(r"\b(" + MON + r")\.?\s+(" + DAYS + r")\b(?:,?\s+(20\d\d)\b)?", re.I)


def _text(page):
    import html as _h
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", page, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", _h.unescape(t))


def _year(txt, pos, end):
    """Jaartal bij de datum: het dichtstbijzijnde jaartal binnen 80 tekens ervoor of erna."""
    lo = max(0, pos - 80)
    near = []
    for m in re.finditer(r"\b20\d\d\b", txt[lo: end + 80]):
        x = lo + m.start()
        near.append((pos - x if x < pos else x - end, int(m.group(0))))
    return min(near)[1] if near else None


def dates(page):
    """[(eerste dag, laatste dag)] van de toekomstige edities die op de pagina staan, meest genoemde eerst."""
    today = date.today().isoformat()
    found = {}
    for o in ld_events(page):
        a, b = str(o.get("startDate", ""))[:10], str(o.get("endDate", "") or o.get("startDate", ""))[:10]
        if re.match(r"\d{4}-\d\d-\d\d$", a) and b >= today:
            found[(a, b)] = found.get((a, b), 0) + 5
    import html as _h
    for txt in (_text(page), re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", " ", page)))):   # ook tekst in scripts
        hits = [(m.group(1), m.group(2), m.group(3), m.start(), m.end()) for m in RANGE.finditer(txt)] + \
               [(m.group(2), m.group(1), m.group(3), m.start(), m.end()) for m in RANGE2.finditer(txt)]
        for ds, mon, y, st, en in hits:
            days = [int(x) for x in re.findall(r"\d{1,2}", ds)]
            mo = MONTHS.get(mon.lower()[:3])
            if not mo or len(days) < 2 or days != sorted(days) or days[0] < 1 or days[-1] - days[0] > 10: continue   # hooguit een dag of tien (Lokerse Feesten)
            y = int(y) if y else _year(txt, st, en)
            if not y: continue
            try:
                a, b = date(y, mo, days[0]).isoformat(), date(y, mo, days[-1]).isoformat()
            except ValueError:
                continue
            if b >= today: found[(a, b)] = found.get((a, b), 0) + 1
        if found: break
    return sorted(found, key=lambda k: (-found[k], k))


# line-up: pagina op de eigen site + hoe de namen erin staan
#   ("link", pad)  = links naar de pagina's van de artiesten (/lineup/naam, /band/naam ...); naam = eerste tekst bij de link
#   ("json", regex) = namen in de gegevens die de pagina zelf meestuurt
LINEUP = {
    "fest_lgw": ("https://leguesswho.nl/lineup", "link", r"/lineup/[^/?#\"]+"),
    "fest_cb": ("https://crossingborder.nl/artists", "json", r'\\"name\\":\\"([^"\\]{2,60})\\",\\"artistImage'),
    "fest_esns": ("https://esns.nl/festival/line-up", "link", r"/(?:en/|nl/)?festival/artists/[^/?#\"]+/?"),
    "fest_roadburn": ("https://roadburn.com/line-up", "link", r"/band/[^/?#\"]+/?"),
    "fest_pinkpop": ("https://www.pinkpop.nl/programma", "link", r"/programma/[^/?#\"]+/?"),
    "fest_bks": ("https://www.bestkeptsecret.nl/program", "link", r"/program/[^/?#\"]+/?"),
    "fest_dynamo": ("https://dynamo-metalfest.nl/line-up", "link", r"/line-up/[^/?#\"]+/?"),
    "fest_itg": ("https://www.intothegrave.nl/line-up", "link", r"/line-up/[^/?#\"]+/?"),
    "fest_motel": ("https://www.motelmozaique.nl/line-up", "link", r"/line-up/[^/?#\"]+/?"),
    "fest_jera": ("https://www.jeraonair.nl/en/line-up", "link", r"/line-up/[^/?#\"]+/?"),
    "fest_pukkelpop": ("https://www.pukkelpop.be/line-up", "link", r"/line-up/[^/?#\"]+/?"),
    "fest_werchter": ("https://www.rockwerchter.be/line-up", "link", r"/line-up/[^/?#\"]+/?"),
    "fest_graspop": ("https://www.graspop.be/line-up", "link", r"/line-up/[^/?#\"]+/?"),
}
NAV = re.compile(r"^(line-?up|programm?a|program|tickets?|meer|more|lees meer|read more|bekijk|view|info|home|nieuws|news|"
                 r"artists?|artiesten|timetable|faq|menu|zoeken|search|alle artiesten|all artists|no matches|geen resultaten|poster|"
                 r"veelgestelde vragen|(mon|tues|wednes|thurs|fri|satur|sun)day|(maan|dins|woens|donder|vrij|zater|zon)dag|curated by .*|\W*)$", re.I)


def lineup(key, a):
    """Namen op de line-up van de editie die op dag 'a' begint, of [] als de pagina (nog) een oude editie laat zien."""
    import html as _h
    if key not in LINEUP: return []
    url, kind, pat = LINEUP[key]
    page = fetch(url, tries=2, timeout=30)
    txt = _text(page)
    y = a[:4]
    # oude editie? Het jaar van deze editie moet op de pagina staan, en het vorige jaar niet vaker (tenzij de data van deze editie er staan)
    prev = txt.count(str(int(y) - 1))   # (het huidige jaar staat ook in de kleine lettertjes onderaan)
    if y not in txt or (prev > 2 * txt.count(y) + 3 and not any(d[0] == a for d in dates(page))):
        return []
    names = []
    if kind == "json":
        names = [_h.unescape(n.encode().decode("unicode_escape", "ignore") if "\\u" in n else n) for n in re.findall(pat, page)]
    else:
        ms = list(re.finditer(r'href="(?:https?://[^/"]+)?(' + pat + r')(?:\?[^"]*)?"', page))
        for i, m in enumerate(ms):
            nxt = ms[i + 1].start() if i + 1 < len(ms) else m.end() + 3000
            st = page.find(">", m.end()) + 1   # vanaf het einde van de link-tag
            for t in re.split(r"<[^>]+>", page[st: min(nxt, st + 3000)]):
                t = re.sub(r"\s+", " ", _h.unescape(t)).strip()
                if t and not NAV.match(t) and not re.match(r"^\d{1,2}\s+\w+$|^(ma|di|wo|do|vr|za|zo|mon|tue|wed|thu|fri|sat|sun)\b", t, re.I):
                    names.append(t); break
    out, seen = [], set()
    for n in names:
        n = re.sub(r"\s+", " ", n).strip(" -–|")
        k = re.sub(r"[^a-z0-9]", "", n.lower())
        if 1 < len(n) <= 60 and k and k not in seen and not NAV.match(n) and not re.search(r'[<>]|="', n):
            seen.add(k); out.append(n)
    return out if len(out) >= 3 else []


def make(key):
    name, city, cc, url = FEST[key]
    def run():
        ds = dates(fetch(url, tries=2, timeout=30))
        if not ds: return []
        a, b = ds[0]
        e = ev(key, a, f"{name} {a[:4]}", url)
        e["e"] = b
        try:
            la = lineup(key, a)
            if la: e["la"], e["lu"] = la, LINEUP[key][0]
        except Exception as ex:
            print(key, "line-up mislukt:", ex)
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
