"""Logo per zaal voor de lijst (in plaats van een letter als een concert geen foto heeft).
Haalt het pictogram dat de zaal zelf op zijn site zet (apple-touch-icon of het grootste icon), maakt er
een vierkant van 112x112 op wit van en zet het in docs/logos/<zaal>.webp. Alleen zalen zonder logo worden
opgehaald; docs/data/logos.json zegt welke er zijn. Gebruik: python tools/logos.py [--force zaal ...]"""
import html as _html, http.cookiejar, io, json, os, re, sys, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scraper"))
from common import fetch, UA  # noqa: E402
from PIL import Image  # noqa: E402

OUT = os.path.join(ROOT, "docs", "logos")
INDEX = os.path.join(ROOT, "docs", "data", "logos.json")
# zelf gekozen logo's: {"zaal": "https://..."} (een plaatje van de eigen site van de zaal); die gaan voor
OWN = os.path.join(ROOT, "data", "logo_urls.json")
SKIP = {"grenswerk", "occii", "vanpolanen", "bos"}   # site-icoon is het standaard WordPress-logo, een foto of wit op wit: dan liever de letter


def venues():
    js = open(os.path.join(ROOT, "docs", "app.js"), encoding="utf-8").read()
    return dict(re.findall(r'^\s*([a-z0-9_]+):\{label:"[^"]*",home:"([^"]+)"', js, re.M))


# met cookies, zoals een browser: sommige zalen (be•at) sturen eerst door naar een stille aanmeldstap
OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def get(u):
    with OPENER.open(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=30) as r:
        return r.read()


def candidates(home):
    try: page = fetch(home, tries=2, timeout=30)
    except Exception: page = get(home).decode("utf-8", "replace")
    found = []
    for tag in re.findall(r"<link\b[^>]*>", page, re.I):
        rel = re.search(r'rel=["\']([^"\']+)', tag, re.I)
        href = re.search(r'href=["\']([^"\']+)', tag, re.I)
        if not rel or not href or "icon" not in rel.group(1).lower(): continue
        u = urllib.parse.urljoin(home, _html.unescape(href.group(1)))
        if u.lower().split("?")[0].endswith(".svg"): continue           # svg kan Pillow niet lezen
        sz = re.search(r'sizes=["\'](\d+)x', tag, re.I)
        size = int(sz.group(1)) if sz else (180 if "apple" in rel.group(1).lower() else 32)
        found.append((size, u))
    found.sort(reverse=True)
    return [u for _, u in found] + [urllib.parse.urljoin(home, "/favicon.ico")]


def load(u):
    if True:
        im = Image.open(io.BytesIO(get(u)))
        if getattr(im, "n_frames", 1) > 1 or im.format == "ICO":
            try: im.size = max(im.info.get("sizes", [im.size]))      # grootste formaat uit een .ico
            except Exception: pass
        im.load()
    return im


def square(im):
    im = im.convert("RGBA")
    box = im.getbbox() or (0, 0) + im.size                            # lege rand weghalen
    im = im.crop(box)
    w, h = im.size; s = max(w, h)
    px = [p for p in im.getdata() if p[3] > 128]                      # wit logo op transparant: donkere achtergrond
    light = px and sum(0.3 * r + 0.59 * g + 0.11 * b for r, g, b, _ in px) / len(px) > 215
    col = (20, 20, 28, 255) if light else (255, 255, 255, 255)
    bg = Image.new("RGBA", (s, s), col)
    bg.alpha_composite(im, ((s - w) // 2, (s - h) // 2))
    pad = int(s * 0.12)                                               # wat lucht rondom
    out = Image.new("RGBA", (s + 2 * pad, s + 2 * pad), col)
    out.alpha_composite(bg, (pad, pad))
    return out.convert("RGB").resize((112, 112), Image.LANCZOS)


def main(force=()):
    os.makedirs(OUT, exist_ok=True)
    try: index = json.load(open(INDEX, encoding="utf-8"))
    except Exception: index = {}
    vs = venues()
    try: own = json.load(open(OWN, encoding="utf-8"))
    except Exception: own = {}
    for k, u in own.items():                                          # eigen keuze: ophalen als die nieuw of gewijzigd is
        if k not in vs or index.get(k + "@") == u: continue
        try:
            square(load(u)).save(os.path.join(OUT, k + ".webp"), "WEBP", quality=80, method=6)
            index[k] = "logos/" + k + ".webp"; index[k + "@"] = u
            print("logo (eigen keuze)", k, u)
        except Exception as e:
            print("eigen logo mislukt", k, u, type(e).__name__)
    for k, home in sorted(vs.items()):
        if k in own and index.get(k + "@") == own[k]: continue
        if k in SKIP:
            index.pop(k, None)
            if os.path.exists(os.path.join(OUT, k + ".webp")): os.remove(os.path.join(OUT, k + ".webp"))
            continue
        if k in index and k not in force and os.path.exists(os.path.join(ROOT, "docs", index[k])): continue
        try:
            for u in candidates(home):
                try: im = load(u)
                except Exception: continue
                if min(im.size) < 32: continue                        # te klein om er iets van te zien
                square(im).save(os.path.join(OUT, k + ".webp"), "WEBP", quality=80, method=6)
                index[k] = "logos/" + k + ".webp"
                print("logo", k, u)
                break
            else:
                print("geen logo", k)
        except Exception as e:
            print("geen logo", k, type(e).__name__)
    index = {k: v for k, v in index.items() if k.rstrip("@") in vs}
    json.dump(index, open(INDEX, "w", encoding="utf-8"), separators=(",", ":"), sort_keys=True)
    print(sum(1 for k in index if not k.endswith("@")), "van", len(vs), "zalen met logo")


if __name__ == "__main__":
    main(force=set(sys.argv[2:]) if sys.argv[1:2] == ["--force"] else ())
