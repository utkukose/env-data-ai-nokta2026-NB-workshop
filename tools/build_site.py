"""Build the bilingual workshop site from the page sources in tools/site_src/.

Each source page holds both languages side by side as ⟪English‖Türkçe⟫.
The build writes docs/<page>.html (English) and docs/tr/<page>.html (Turkish),
renders every formula with KaTeX ahead of time, and fills numbers written as
{{n:path:digits}} from docs/assets/site-data.js with the decimal mark of the
language. Run after tools/build_site_data.py:

    python tools/build_site.py
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tools" / "site_src"
DOCS = ROOT / "docs"
OWNER, REPO = "utkukose", "env-data-ai-nokta2026-NB-workshop"
SITE = f"https://{OWNER}.github.io/{REPO}/"
NB = {"en": "notebooks/NOKTA_AI_Workshop_EN.ipynb", "tr": "notebooks/NOKTA_AI_Workshop_TR.ipynb"}
COLAB = {k: f"https://colab.research.google.com/github/{OWNER}/{REPO}/blob/main/{v}"
         for k, v in NB.items()}
KATEX = Path(__file__).resolve().parent / "node"   # run "npm install" there once
PAGES = ["index", "part1", "part2", "part3", "part4", "part5", "lab"]
ROUTE = {
    "en": ["Start", "1 Measure", "2 Analyze", "3 Discover", "4 Explain", "5 Share", "Lab"],
    "tr": ["Başlangıç", "1 Ölç", "2 Analiz et", "3 Keşfet", "4 Açıkla", "5 Paylaş", "Laboratuvar"],
}
ROUTE_TITLE = {
    "en": ["Start", "Part 1 · Measure", "Part 2 · Analyze", "Part 3 · Discover", "Part 4 · Explain", "Part 5 · Share and act", "NOKTA Lab"],
    "tr": ["Başlangıç", "1. Bölüm · Ölç", "2. Bölüm · Analiz et", "3. Bölüm · Keşfet", "4. Bölüm · Açıkla", "5. Bölüm · Paylaş ve aksiyona dönüştür", "NOKTA Laboratuvarı"],
}
TOKEN = re.compile(r"⟪(.*?)‖(.*?)⟫", re.S)



# ------------------------------------------------ measurement plan (shared by several pages)
PLAN_SLOTS = [("10:00", "10:15", 1, 6), ("10:25", "10:40", 2, 5), ("10:50", "11:05", 3, 4),
              ("11:15", "11:30", 4, 3), ("11:40", "11:55", 5, 2), ("12:05", "12:20", 6, 1)]
PLAN_NAMES = {1: "⟪Shaded‖Gölgeli⟫", 2: "⟪Traffic‖Trafik⟫", 3: "⟪Reference‖Referans⟫",
              4: "⟪Sunny‖Güneşli⟫", 5: "⟪Busy‖Yoğun⟫", 6: "⟪Green‖Yeşil⟫"}


def _pt(n):
    return f'<i class="sw" style="background:var(--t{n})"></i>P{n} · {PLAN_NAMES[n]}'


def plan_html():
    """Clock times and order of the visits in both rounds, plus the dates per campus."""
    rows = "".join(
        f'<tr><td class="t">⟪{a} to {b}‖{a}-{b}⟫</td><td>{_pt(p1)}</td><td>{_pt(p2)}</td></tr>'
        for a, b, p1, p2 in PLAN_SLOTS)
    return (
        '<div class="plan-box">'
        '<table class="tbl plan"><thead><tr><th>⟪Clock time‖Saat⟫</th>'
        "<th>⟪Round 1: from P1 to P6‖1. tur: P1'den P6'ya⟫</th>"
        "<th>⟪Round 2, one week later: from P6 to P1‖2. tur, bir hafta sonra: P6'dan P1'e⟫</th>"
        f"</tr></thead><tbody>{rows}</tbody></table>"
        '<table class="tbl plan plan-dates"><thead><tr><th>⟪Campus‖Kampüs⟫</th>'
        "<th>⟪Day of Round 1‖1. turun günü⟫</th><th>⟪Day of Round 2‖2. turun günü⟫</th></tr></thead><tbody>"
        "<tr><td>⟪A · about 1000 m above sea level‖A · deniz seviyesinden yaklaşık 1000 m yukarıda⟫</td>"
        "<td>⟪11 November‖11 Kasım⟫</td><td>⟪18 November‖18 Kasım⟫</td></tr>"
        "<tr><td>⟪B · city campus‖B · şehir kampüsü⟫</td><td>⟪12 November‖12 Kasım⟫</td><td>⟪19 November‖19 Kasım⟫</td></tr>"
        "<tr><td>⟪C · coastal campus‖C · kıyı kampüsü⟫</td><td>⟪10 November‖10 Kasım⟫</td><td>⟪17 November‖17 Kasım⟫</td></tr>"
        "</tbody></table>"
        '<p class="note">⟪Each visit lasts 15 minutes, and the station takes one reading every 10 seconds. Walking to the next point takes 10 minutes. '
        "The first two minutes of every visit are left out of all calculations, because the sensors are still adjusting to the new place. "
        "Thirteen minutes of every visit are therefore analyzed.‖"
        "Her ziyaret 15 dakika sürer ve istasyon her 10 saniyede bir ölçüm alır. Bir sonraki noktaya yürümek 10 dakika sürer. "
        "Her ziyaretin ilk iki dakikası hiçbir hesaba katılmaz, çünkü sensörler bu sırada yeni yere uyum sağlamaya çalışmaktadır. "
        "Bu yüzden her ziyaretin 13 dakikası analiz edilir.⟫</p></div>")


def plan_fair_html():
    """Clock times of the two visits of each point and their mean."""
    t1 = {p1: a for a, b, p1, p2 in PLAN_SLOTS}
    t2 = {p2: a for a, b, p1, p2 in PLAN_SLOTS}
    rows = "".join(
        f'<tr><td>{_pt(n)}</td><td class="t">{t1[n]}</td><td class="t">{t2[n]}</td><td class="t"><b>11:02:30</b></td></tr>'
        for n in range(1, 7))
    return (
        '<div class="plan-box"><table class="tbl plan"><thead><tr><th>⟪Point‖Nokta⟫</th>'
        "<th>⟪Start in Round 1‖1. turda başlangıç⟫</th><th>⟪Start in Round 2‖2. turda başlangıç⟫</th>"
        f"<th>⟪Mean of the two‖İkisinin ortalaması⟫</th></tr></thead><tbody>{rows}</tbody></table>"
        '<p class="note">⟪A point measured early in Round 1 is measured late in Round 2. For every point, the mean of its two start times is the same, 11:02:30.‖'
        "1. turda erken ölçülen bir nokta 2. turda geç ölçülür. Bu yüzden her noktanın iki başlangıç saatinin ortalaması aynıdır: 11:02:30.⟫</p></div>")

def lang_pick(text, lang):
    return TOKEN.sub(lambda m: m.group(1) if lang == "en" else m.group(2), text)


def load_data():
    js = (DOCS / "assets" / "site-data.js").read_text(encoding="utf-8")
    return json.loads(js[js.index("{"):js.rstrip().rstrip(";").rindex("}") + 1])


def lookup(data, path):
    cur = data
    for k in path.split("."):
        cur = cur[int(k)] if isinstance(cur, list) else cur[k]
    return cur


def fmt_num(x, nd, lang, tex=False, signed=False):
    if round(x, nd) == 0:
        x = 0.0
    s = f"{abs(x) if signed else x:,.{nd}f}"
    if lang == "tr":
        s = s.replace(",", "§").replace(".", ",").replace("§", ".")
        if tex:
            s = s.replace(",", "{,}")
    elif tex:
        s = s.replace(",", "{,}")
    if signed:
        s = ("+" if x > 0 else "−" if x < 0 else "") + s
    elif not tex and s.startswith("-"):
        s = "−" + s[1:]
    return s


def fill_numbers(text, data, extra, lang):
    def rep(m):
        kind, path, nd = m.group(1), m.group(2), int(m.group(3))
        val = extra[path] if path in extra else lookup(data, path)
        return fmt_num(float(val), nd, lang, tex=(kind == "t"), signed=(kind == "s"))
    return re.sub(r"\{\{([nts]):([\w.\-]+):(\d)\}\}", rep, text)


def render_tex(items):
    tmp_in, tmp_out = Path("/tmp/tex_in.json"), Path("/tmp/tex_out.json")
    tmp_in.write_text(json.dumps(items), encoding="utf-8")
    subprocess.run(["node", str(KATEX / "render_tex.js"), str(tmp_in), str(tmp_out)],
                   check=True, cwd=KATEX)
    return json.loads(tmp_out.read_text(encoding="utf-8"))


def worked_examples(data):
    """Numbers of the worked examples, computed here so that text and code agree."""
    ex = {}
    x = [14.2, 15.0, 13.8, 14.6, 97.3, 15.1, 14.4]
    med = sorted(x)[3]
    dev = [abs(v - med) for v in x]
    mad = sorted(dev)[3]
    mean = round(sum(x) / len(x), 2)
    sd = round(math.sqrt(sum((v - mean) ** 2 for v in x) / len(x)), 2)
    ex.update({"z.med": med, "z.mad": mad, "z.dev": round(97.3 - med, 1),
               "z.M": round(0.6745 * round(97.3 - med, 1) / mad, 2),
               "z.mean": mean, "z.sd": sd, "z.z": round((97.3 - mean) / sd, 2),
               "z.M2": round(0.6745 * abs(15.1 - med) / mad, 2)})
    # humidity correction for the green area of Campus C, round 2
    hc = [h for h in data["humidity"]["campusC_round2"] if h["type"] == "green"][0]
    aw = round(hc["rh"] / 100, 3)
    inv = round(-1 + 1 / aw, 3)
    kr = round(0.3 / 1.65, 3)
    c = round(1 + kr / inv, 3)
    ex.update({"h.rh": hc["rh"], "h.aw": aw, "h.inv": inv, "h.kr": kr, "h.c": c,
               "h.raw": hc["raw"], "h.cor": round(hc["raw"] / c, 1),
               "h.corrected_pipeline": hc["corrected"]})
    # co-location: first minute of the side-by-side test
    s = data["coloc"]["series"]["temperature_c"]
    v1, v2, v3 = s["S1"][0], s["S2"][0], s["S3"][0]
    m3 = round((v1 + v2 + v3) / 3, 2)
    ex.update({"c.s1": v1, "c.s2": v2, "c.s3": v3, "c.mean": m3,
               "c.d1": round(v1 - m3, 2), "c.d2": round(v2 - m3, 2), "c.d3": round(v3 - m3, 2)})
    # fair comparison for Campus A, temperature
    fa = {r["type"]: r for r in data["fair"]["temperature_c"] if r["campus"] == "A"}
    for t in ["green", "traffic", "reference", "shaded", "sunny_hard", "crowded"]:
        ex[f"f.{t}.r1"] = fa[t]["r1"]
        ex[f"f.{t}.r2"] = fa[t]["r2"]
        ex[f"f.{t}.mean"] = round((fa[t]["r1"] + fa[t]["r2"]) / 2, 2)
    for t in ["green", "traffic", "shaded", "sunny_hard", "crowded"]:
        ex[f"f.{t}.ref"] = round(ex[f"f.{t}.mean"] - ex["f.reference.mean"], 2)
    # dew point example
    tt, rh = 13.3, 43.0
    gam1 = round(math.log(rh / 100), 3)
    gam2 = round(17.625 * tt / (243.04 + tt), 3)
    gam = round(gam1 + gam2, 3)
    td = round(243.04 * gam / (17.625 - gam), 1)
    ex.update({"d.t": tt, "d.rh": rh, "d.g1": gam1, "d.g2": gam2, "d.g": gam, "d.td": td})
    # standardisation and nearest centre for one sunny minute (k = 4)
    mu, sd4 = data["cluster"]["mu"], data["cluster"]["sd"]
    xm = [3.2, 4.8, 0.5]
    zz = [round((xm[i] - mu[i]) / sd4[i], 2) for i in range(3)]
    ex.update({"k.x0": xm[0], "k.x1": xm[1], "k.x2": xm[2], "k.mu0": mu[0], "k.sd0": sd4[0],
               "k.z0": zz[0], "k.z1": zz[1], "k.z2": zz[2]})
    cen = data["cluster"]["centers"]["4"]
    dists = [round(math.sqrt(sum((zz[i] - c4[i]) ** 2 for i in range(3))), 2) for c4 in cen]
    for j, d in enumerate(dists):
        ex[f"k.d{j}"] = d
    ex["k.best"] = dists.index(min(dists)) + 1
    # R2 drop
    cv = data["rf"]["cv"]
    ex["rf.drop"] = round(100 * (cv["random"] - cv["group"]) / cv["random"])
    return ex


ICONS = {
    "theme": "<svg class='ic' viewBox='0 0 24 24' aria-hidden='true'><circle cx='12' cy='12' r='8.5'/><path class='f' d='M12 3.5a8.5 8.5 0 0 0 0 17z'/></svg>",
    "full": "<svg class='ic' viewBox='0 0 24 24' aria-hidden='true'><path d='M4 9V4h5M15 4h5v5M20 15v5h-5M9 20H4v-5'/></svg>",
    "help": "<svg class='ic' viewBox='0 0 24 24' aria-hidden='true'><circle cx='12' cy='12' r='9'/><path d='M9.4 9.4a2.7 2.7 0 1 1 3.8 2.5c-.8.4-1.2 1-1.2 1.8v.5'/><circle class='f' cx='12' cy='17' r='1.2'/></svg>",
    "close": "<svg class='ic' viewBox='0 0 24 24' aria-hidden='true'><path d='M6 6l12 12M18 6L6 18'/></svg>",
    "ext": "<svg class='ic' viewBox='0 0 24 24' aria-hidden='true'><path d='M8 16L16 8M9.5 8H16v6.5'/></svg>",
    "play": "<svg class='ic' viewBox='0 0 24 24' aria-hidden='true'><path class='f' d='M8 5.5v13l10.5-6.5z'/></svg>",
    "pause": "<svg class='ic' viewBox='0 0 24 24' aria-hidden='true'><path class='f' d='M7 5h3.6v14H7zM13.4 5H17v14h-3.6z'/></svg>",
    "reset": "<svg class='ic' viewBox='0 0 24 24' aria-hidden='true'><path d='M4.5 12a7.5 7.5 0 1 0 2.2-5.3'/><path d='M4.5 4.5v4.6h4.6'/></svg>",
    "globe": "<svg class='ic' viewBox='0 0 24 24' aria-hidden='true'><circle cx='12' cy='12' r='9'/><path d='M3 12h18M12 3c2.6 2.8 3.9 5.8 3.9 9s-1.3 6.2-3.9 9M12 3c-2.6 2.8-3.9 5.8-3.9 9s1.3 6.2 3.9 9'/></svg>",
    "check": "<svg class='ic' viewBox='0 0 24 24' aria-hidden='true'><path d='M5 12.5l4.5 4.5L19 7.5'/></svg>",
    "cross": "<svg class='ic' viewBox='0 0 24 24' aria-hidden='true'><path d='M7 7l10 10M17 7L7 17'/></svg>",
}


def put_icons(text):
    """Replaces {{ICON:name}} placeholders and the external-link arrow with inline SVG icons."""
    text = re.sub(r"\{\{ICON:(\w+)\}\}", lambda m: ICONS[m.group(1)], text)
    return text.replace("↗", ICONS["ext"])


def page_shell(lang, page, meta, body):
    a = "assets/" if lang == "en" else "../assets/"
    other = ("tr/" if lang == "en" else "../") + f"{page}.html"
    route = "".join(
        f'<li data-page="{p}"><a href="{p}.html" title="{ROUTE_TITLE[lang][i]}"><span class="pin"></span>'
        f'<span class="lbl">{ROUTE[lang][i]}</span></a></li>' for i, p in enumerate(PAGES))
    help_txt = lang_pick(
        "⟪Keys‖Tuşlar⟫</h3><p><kbd>←</kbd> <kbd>→</kbd> ⟪previous or next station‖önceki ya da sonraki durak⟫ · "
        "<kbd>[</kbd> <kbd>]</kbd> ⟪previous or next part‖önceki ya da sonraki bölüm⟫ · <kbd>T</kbd> ⟪paper or night view‖kâğıt ya da gece görünümü⟫ · "
        "<kbd>F</kbd> ⟪full screen‖tam ekran⟫ · <kbd>L</kbd> ⟪English or Turkish‖İngilizce ya da Türkçe⟫ · <kbd>B</kbd> ⟪five-minute break‖beş dakikalık ara⟫ · "
        "<kbd>?</kbd> ⟪this help‖bu yardım⟫</p>", lang)
    sig = lang_pick(
        '<b>Prof. Dr. Utku Köse</b><br>⟪Süleyman Demirel University, AI Application and Research Center (YAZEM)‖Süleyman Demirel Üniversitesi, Yapay Zekâ Uygulama ve Araştırma Merkezi (YAZEM)⟫'
        ' · University of North Dakota · Universidad Panamericana · Vel Tech University<br>'
        '<a href="https://www.utkukose.com">utkukose.com</a> · <a href="https://orcid.org/0000-0002-9652-6415">ORCID 0000-0002-9652-6415</a> · '
        '<a href="https://github.com/utkukose">github.com/utkukose</a><br>'
        '⟪NOKTA, Objective Measurement, Participation, Monitoring and Action Network · ÜNİDES 2026‖NOKTA, Nesnel Ölçüm, Katılım, Takip ve Aksiyon Ağı · ÜNİDES 2026⟫<br>'
        '⟪This workshop is updated in line with current developments in the field. First version: November 2026.‖Bu atölye alandaki güncel gelişmelere göre güncellenmektedir. İlk sürüm: Kasım 2026.⟫<br>'
        '⟪Content: CC BY 4.0 · Code: MIT · The data are synthetic and describe no real campus.‖İçerik: CC BY 4.0 · Kod: MIT · Veriler sentetiktir ve gerçek bir kampüsü anlatmaz.⟫', lang)
    nxt = meta.get("next")
    next_html = f'<a class="btn primary next" href="{nxt[0]}.html">{lang_pick(nxt[1], lang)} →</a><br>' if nxt else ""
    title = lang_pick(meta["title"], lang)
    desc = lang_pick(meta.get("desc", ""), lang)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="{a}vendor/fonts/atkinson.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230E7A5F'/%3E%3Ccircle cx='32' cy='32' r='11' fill='white'/%3E%3Ccircle cx='32' cy='32' r='20' fill='none' stroke='white' stroke-width='4' stroke-dasharray='6 6'/%3E%3C/svg%3E">
<link rel="stylesheet" href="{a}vendor/katex/katex.min.css">
<link rel="stylesheet" href="{a}site.css">
<script src="{a}site-data.js"></script>
<script src="{a}site.js"></script>
<script src="{a}charts.js"></script>
{'<script src="' + a + 'vendor/three.bundle.min.js"></script><script src="' + a + 'nokta3d.js"></script>' if meta.get("three") else ''}
</head>
<body data-part="{meta.get('part', 'start')}">
<header class="topbar"><div class="wrap">
<a class="brand" href="index.html"><span class="dot"></span><span class="name">NOKTA · {lang_pick('⟪AI workshop‖YZ atölyesi⟫', lang)}<small>{lang_pick('⟪Environmental data analysis and interpretation‖Çevresel veri analizi ve yorumlama⟫', lang)}</small></span></a>
<nav class="route" aria-label="{lang_pick('⟪Workshop route‖Atölye rotası⟫', lang)}"><ol>{route}</ol></nav>
<div class="tools"><a class="lang" href="{other}" hreflang="{'tr' if lang == 'en' else 'en'}" lang="{'tr' if lang == 'en' else 'en'}" title="{lang_pick('⟪Bu sayfanın Türkçesi (L)‖English version of this page (L)⟫', lang)}">{ICONS['globe']}<span class="long">{'Türkçe' if lang == 'en' else 'English'}</span><span class="short">{'TR' if lang == 'en' else 'EN'}</span></a>
<button data-act="theme" title="{lang_pick('⟪Paper or night view (T)‖Kâğıt ya da gece görünümü (T)⟫', lang)}" aria-label="{lang_pick('⟪Paper or night view‖Kâğıt ya da gece görünümü⟫', lang)}">{ICONS['theme']}</button><button data-act="full" title="{lang_pick('⟪Full screen (F)‖Tam ekran (F)⟫', lang)}" aria-label="{lang_pick('⟪Full screen‖Tam ekran⟫', lang)}">{ICONS['full']}</button><button data-act="help" title="{lang_pick('⟪Keys (?)‖Tuşlar (?)⟫', lang)}" aria-label="{lang_pick('⟪Keys‖Tuşlar⟫', lang)}">{ICONS['help']}</button></div>
</div></header>
<main>
{body}
</main>
<footer class="sig"><div class="wrap">{next_html}{sig}</div></footer>
<div class="overlay" id="help-overlay" hidden><div class="box"><button class="btn close" data-act="close" aria-label="{lang_pick('⟪Close‖Kapat⟫', lang)}">{ICONS['close']}</button><h3>{help_txt}</div></div>
<div class="overlay" id="break-overlay" hidden><div class="box"><button class="btn close" data-act="close" aria-label="{lang_pick('⟪Close‖Kapat⟫', lang)}">{ICONS['close']}</button>
<p class="kicker">{lang_pick('⟪Break‖Ara⟫', lang)}</p><div class="breakclock">5:00</div>
<p class="lead" style="text-align:center;margin:14px auto 0">{lang_pick('⟪Question for after the break: Which of the six points do you expect to look warmest in Round 1, and why might that be misleading?‖Aradan sonraki soru: 1. turda altı noktadan hangisinin en sıcak görüneceğini düşünüyorsunuz ve bu neden yanıltıcı olabilir?⟫', lang)}</p></div></div>
</body>
</html>
"""


def build():
    data = load_data()
    extra = worked_examples(data)
    (DOCS / "tr").mkdir(parents=True, exist_ok=True)
    outputs = {}
    tex_items, tex_slots = [], []
    for page in PAGES:
        src = (SRC / f"{page}.html").read_text(encoding="utf-8")
        mm = re.match(r"<!--META(.*?)-->", src, re.S)
        meta = json.loads(mm.group(1))
        body = src[mm.end():]
        body = body.replace("{{PLAN}}", plan_html()).replace("{{PLAN_FAIR}}", plan_fair_html())
        for lang in ("en", "tr"):
            text = lang_pick(body, lang)
            text = fill_numbers(text, data, extra, lang)
            text = (text.replace("{{COLAB}}", COLAB[lang]).replace("{{SITE}}", SITE)
                    .replace("{{REPO}}", f"https://github.com/{OWNER}/{REPO}")
                    .replace("{{NBFILE}}", NB[lang].split("/")[-1]))
            text = put_icons(text)
            for mt in re.finditer(r"<(texd|tex)>(.*?)</\1>", text, re.S):
                tex_items.append({"tex": mt.group(2).strip(), "display": mt.group(1) == "texd"})
            outputs[(page, lang)] = (meta, text)
    rendered = render_tex(tex_items)
    it = iter(rendered)
    for (page, lang), (meta, text) in outputs.items():
        text = re.sub(r"<(texd|tex)>(.*?)</\1>", lambda m: next(it), text, flags=re.S)
        leftover = TOKEN.findall(text) or re.findall(r"\{\{[nts]:", text)
        if leftover:
            raise SystemExit(f"unresolved tokens in {page}/{lang}: {leftover[:3]}")
        html = page_shell(lang, page, meta, text)
        target = DOCS / (f"{page}.html" if lang == "en" else f"tr/{page}.html")
        target.write_text(html, encoding="utf-8")
    (ROOT / "tools" / "worked_examples.json").write_text(json.dumps(extra, indent=1), encoding="utf-8")
    print("built", len(outputs), "pages,", len(tex_items), "formulas")


if __name__ == "__main__":
    build()
