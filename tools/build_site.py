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
    "en": ["Start", "1 Measure", "2 Analyze", "3 Discover", "4 Explain", "5 Share and act", "Lab"],
    "tr": ["Başlangıç", "1 Ölç", "2 Analiz et", "3 Keşfet", "4 Açıkla", "5 Paylaş ve dönüştür", "Laboratuvar"],
}
TOKEN = re.compile(r"⟪(.*?)‖(.*?)⟫", re.S)


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


def page_shell(lang, page, meta, body):
    a = "assets/" if lang == "en" else "../assets/"
    other = ("tr/" if lang == "en" else "../") + f"{page}.html"
    route = "".join(
        f'<li data-page="{p}"><a href="{p}.html"><span class="pin"></span>'
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
<div class="tools"><a class="lang" href="{other}" title="{lang_pick('⟪Türkçe sürüm‖English version⟫', lang)}">{'TR' if lang == 'en' else 'EN'}</a>
<button data-act="theme" title="T">◐</button><button data-act="full" title="F">⛶</button><button data-act="help" title="?">?</button></div>
</div></header>
<main>
{body}
</main>
<footer class="sig"><div class="wrap">{next_html}{sig}</div></footer>
<div class="overlay" id="help-overlay" hidden><div class="box"><button class="btn close" data-act="close">✕</button><h3>{help_txt}</div></div>
<div class="overlay" id="break-overlay" hidden><div class="box"><button class="btn close" data-act="close">✕</button>
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
        for lang in ("en", "tr"):
            text = lang_pick(body, lang)
            text = fill_numbers(text, data, extra, lang)
            text = (text.replace("{{COLAB}}", COLAB[lang]).replace("{{SITE}}", SITE)
                    .replace("{{REPO}}", f"https://github.com/{OWNER}/{REPO}")
                    .replace("{{NBFILE}}", NB[lang].split("/")[-1]))
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
