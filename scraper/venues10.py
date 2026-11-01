"""November 2026: Oberhausen (Duitsland) - Turbinenhalle, Kulttempel, Rudolf Weber-Arena, Zentrum Altenberg, Druckluft en Helvete.
Alles van de eigen sites van de zalen."""
import re
from datetime import date
from common import *

DE_MONTHS = {"jan": 1, "feb": 2, "mär": 3, "mar": 3, "apr": 4, "mai": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "okt": 10, "nov": 11, "dez": 12}


def _ld(key, url, skip=None):
    """schema.org-evenementen van een lijstpagina; datums soms zonder voorloopnul ('2026-11-5T18:30+1:00')."""
    out = []
    for o in ld_events(fetch(url)):
        m = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})(?:T(\d{1,2}):(\d\d))?", str(o.get("startDate", "")))
        name = clean(o.get("name", ""))
        if not m or not name or cancelled(o) or (skip and re.search(skip, name, re.I)): continue
        d = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
        tm = f"{int(m.group(4)):02d}:{m.group(5)}" if m.group(4) else ""
        room = clean((o.get("location") or {}).get("name", "")) if isinstance(o.get("location"), dict) else ""
        out.append(ev(key, d, name, o.get("url") or url, tm, room, sold_from_offers(o)))
    return out


def turbinenhalle():   # programma met schema.org per avond; geen feesten en kermis
    return _ld("turbinenhalle", "https://turbinenhalle.de/programm/", r"\bparty\b|\bkirmes\b|\bflohmarkt\b|\bmesse\b|\bü\s?30\b|\bclubnacht\b")


def altenberg():   # alleen de categorie 'Konzerte'; poetry slam en kabarett staan in een andere categorie
    return _ld("altenberg", "https://www.zentrumaltenberg.de/konzerte/", r"poetry slam|kabarett|comedy|lesung")


def helvete():   # metalclub; muziekwedstrijd (SPH Music Masters) telt niet als concert
    return _ld("helvete", "https://helvete.de/events/", r"music masters|\bparty\b|karaoke|quiz|^halloween$")


def kulttempel():
    """Kulttempel: alles staat op de voorpagina met een categorie per item; alleen 'Konzert' (geen feesten, sport, comedy, rommelmarkt)."""
    page, out = fetch("https://www.kulttempel.com/"), []
    for blk in re.split(r'(?=<div class="el-item-\d+-container fs-load-more-item")', page)[1:]:
        tag = re.search(r'data-tag="([^"]*)"', blk)
        if not tag or tag.group(1) != "Konzert": continue
        t = re.search(r'<h3 class="el-title[^"]*">(.*?)</h3>', blk, re.S)
        d = re.search(r'dp-date__start">\w+, (\d\d)\.(\d\d)\.(\d{4})</span>\s*(?:<span class="dp-time__start">-\s*(\d\d:\d\d))?', blk)
        u = re.search(r"href='(https://www\.kulttempel\.com/kkt-kalender/[^']+)'", blk)
        if not (t and d): continue
        out.append(ev("kulttempel", f"{d.group(3)}-{d.group(2)}-{d.group(1)}", re.sub(r"<[^>]+>", "", t.group(1)), u.group(1) if u else "https://www.kulttempel.com/", d.group(4) or ""))
    return out


def rwa():
    """Rudolf Weber-Arena: lijst met titel, ondertitel en '01.11.2026 | 19:30 Uhr'. Geen ijsshows, sport of comedy."""
    page, out, had = fetch("https://www.rudolf-weber-arena.de/events-tickets/events/"), [], set()
    for m in re.finditer(r'<div data-href="([^"]+)"\s+class="event-item[^"]*".*?<h3>(.*?)</h3>\s*(?:<h4>(.*?)</h4>)?\s*<h5>(\d\d)\.(\d\d)\.(\d{4})<span class="pipe"></span>\s*(?:(\d\d:\d\d) Uhr)?', page, re.S):
        title, sub = clean(m.group(2)), clean(m.group(3) or "")
        if re.search(r"on ice|holiday on ice|comedy|kabarett|eishockey|handball|basketball|boxen|wrestling|darts|messe|musical|zirkus|circus|padel|let.s dance|ehrlich brothers|zauber|magie|lesung|vortrag|ballett|tanzshow|laugh|nuhr", title + " " + sub, re.I): continue
        # de arena heeft geen categorieën: muziek herken je aan de ondertitel (tour, concert, live ...) of aan een lege ondertitel;
        # comedians hebben hier de titel van hun programma ('Schmitzmän', 'Wok-Life-Balance')
        if sub and not re.search(r"tour|tournee|concert|konzert|live|show|festival|anniversary|jubil", sub, re.I): continue
        if (m.group(1), m.group(4)) in had: continue   # lijst- en tegelweergave staan allebei in de pagina
        had.add((m.group(1), m.group(4)))
        out.append(ev("rwa", f"{m.group(6)}-{m.group(5)}-{m.group(4)}", title, m.group(1), m.group(7) or "", sold="ausverkauft" in page[m.end():m.end() + 400].lower()))
    return out


def druckluft():
    """Druckluft (jongeren- en cultuurcentrum): uitklaplijst met 'Dienstag, 03 Nov 2026', '18:00 Uhr' en titel.
    Geen café, lezing, poetry slam, open podium, comedy of spelmiddag."""
    page, out = fetch("https://drucklufthaus.de/veranstaltungen/"), []
    for m in re.finditer(r'<h4>\w+, (\d\d) (\w{3})\w* (\d{4})</h4>\s*<h4>\s*(\d\d:\d\d)?[^<]*</h4>\s*</div>\s*<h2>(.*?)</h2>', page, re.S):
        mm = DE_MONTHS.get(m.group(2).lower()[:3])
        title = clean(re.sub(r"<[^>]+>", "", m.group(5)))
        if not mm or not title: continue
        if re.search(r"caf[ée]\b|lesung|silent reading|poetry|slam|open stage|comedy|impro|spielenachmittag|treasures|wave party|\bparty$", title, re.I): continue
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40]
        out.append(ev("druckluft", f"{m.group(3)}-{mm:02d}-{m.group(1)}", title, f"https://drucklufthaus.de/veranstaltungen/#{m.group(1)}{mm:02d}-{slug}", m.group(4) or ""))
    return out
