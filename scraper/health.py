"""Bewaking van de zalen: meldt een zaal die niet meer werkt, opeens veel minder concerten heeft
of al dagen op een oude reservelijst draait. Resultaat in events.json ("alerts") voor de infopagina
en in data/alerts.md voor de melding op GitHub (zie .github/workflows/update.yml)."""
import json, os, re
from datetime import date, timedelta

DROP = 0.5        # minder dan de helft van het gewone aantal = melding
MIN_BASE = 10     # alleen bij zalen die normaal minstens zoveel concerten hebben
ACCEPT_DAYS = 7   # blijft het lagere aantal een week zo, dan is dat het nieuwe normaal


def labels(root):
    try:
        js = open(os.path.join(root, "docs", "app.js"), encoding="utf-8").read()
        return dict(re.findall(r'^\s*([a-z0-9_]+):\{label:"([^"]+)"', js, re.M))
    except Exception:
        return {}


def check(status, data_dir, root, min_events, skip=("ticketswap",)):
    hp = os.path.join(data_dir, "health.json")
    try:
        health = json.load(open(hp, encoding="utf-8"))
    except Exception:
        health = {}
    today = date.today()
    t = today.isoformat()
    names = labels(root)
    alerts = []
    for key, st in sorted(status.items()):
        if key in skip: continue
        h = health.setdefault(key, {})
        cnt = st.get("count") or 0
        why = ""
        if not st.get("ok"):
            why = "werkt niet: " + (st.get("error") or "onbekende fout")[:140]
        elif st.get("manual") and key != "tivoli" and (st.get("checked") or "") < (today - timedelta(days=3)).isoformat():
            why = "draait op een oude reservelijst van de pc (" + (st.get("checked") or "?") + ")"
        elif min_events.get(key, 3) > 0 and h.get("good", 0) >= MIN_BASE and cnt < DROP * h["good"]:
            why = f"veel minder concerten: normaal {h['good']}, nu {cnt}"
            if h.get("since") and h["since"] <= (today - timedelta(days=ACCEPT_DAYS)).isoformat() and cnt > 0:
                h["good"] = cnt; why = ""          # al een week zo: geaccepteerd als nieuw normaal
        if why:
            h.setdefault("since", t)
            # pas melden als het probleem er de vorige dag ook al was: een storing van één run is normaal
            if h["since"] < t:
                alerts.append({"v": key, "name": names.get(key, key), "why": why, "since": h["since"]})
        else:
            h.pop("since", None)
            if st.get("ok") and not st.get("manual"):
                h["good"] = cnt
    for k in [k for k in health if k not in status and not k.startswith("_")]:
        del health[k]
    keys = sorted(a["v"] for a in alerts)
    changed = keys != health.get("_last", [])
    health["_last"] = keys
    json.dump(health, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
    flag = os.path.join(data_dir, "alerts.changed")   # voor de melding op GitHub: alleen een bericht als de lijst echt verandert
    if changed: open(flag, "w").write("1")
    elif os.path.exists(flag): os.remove(flag)
    md = os.path.join(data_dir, "alerts.md")
    if alerts:
        lines = ["@bzwijgers, de dagelijkse update vond problemen bij deze zalen:", ""]
        lines += [f"- **{a['name']}** (`{a['v']}`): {a['why']} — sinds {a['since']}" for a in alerts]
        lines += ["", "De laatst bekende concerten van deze zalen blijven in de agenda staan. "
                  "Deze melding wordt automatisch bijgewerkt en gesloten zodra alles weer werkt."]
        open(md, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    elif os.path.exists(md):
        os.remove(md)
    print("bewaking:", len(alerts), "melding(en)", [a["v"] for a in alerts])
    return alerts
