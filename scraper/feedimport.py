"""Leest de openbare feed van het bestaande project (bzwijgers/barrys-concert-agenda, concerts.json).
Die feed wordt door de eigenaar zelf uit de zaalsites opgebouwd. Gebruikt voor Tivoli, dB's en exacte TicketSwap-links."""
import json, re, urllib.request
URL = "https://raw.githubusercontent.com/bzwijgers/barrys-concert-agenda/main/concerts.json"


def norm_url(u):
    u = (u or "").lower().split("#")[0].split("?")[0].rstrip("/")
    return re.sub(r"^https?://(www\.)?", "", u)


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", "", (t or "").lower())


def load():
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "BarrysConcertAgenda/1.0 (persoonlijk gebruik)"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode("utf-8"))
        return data if isinstance(data, list) else None
    except Exception as ex:
        print("feed niet beschikbaar:", ex)
        return None


def events_for(feed, source, key):
    out = []
    for x in feed:
        if x.get("source") != source or not x.get("date") or not x.get("url"): continue
        out.append({"v": key, "d": x["date"], "n": x.get("artist", ""), "u": x["url"], "t": x.get("time", "") or "",
                    "r": "", "s": False, "c": False, **({"k": x["ticketSwapUrl"]} if x.get("ticketSwapUrl") else {})})
    return out


def ticketswap_index(feed):
    by_url, by_dt = {}, {}
    for x in feed:
        k = x.get("ticketSwapUrl")
        if not k: continue
        by_url[norm_url(x.get("url"))] = k
        by_dt.setdefault((x.get("date"), norm_title(x.get("artist"))), k)
    return by_url, by_dt


def attach_ticketswap(events, feed):
    by_url, by_dt = ticketswap_index(feed)
    n = 0
    for e in events.values():
        if e.get("k"): continue
        k = by_url.get(norm_url(e["u"])) or by_dt.get((e["d"], norm_title(e["n"])))
        if k:
            e["k"] = k; n += 1
    print("TicketSwap-links uit feed:", n)
