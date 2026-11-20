"""Build the English and Turkish Colab notebooks of the workshop.

Markdown and code are written once, with both languages side by side as
⟪English‖Türkçe⟫. The analysis functions are copied from tools/nokta_core.py,
so the notebooks, the site data and the pages share one implementation.

Run:  python tools/build_notebooks.py
"""
import inspect
import re
import sys
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import nokta_core as core  # noqa: E402

OWNER, REPO = "utkukose", "env-data-ai-nokta2026-NB-workshop"
SITE = f"https://{OWNER}.github.io/{REPO}/"
TOKEN = re.compile(r"⟪(.*?)‖(.*?)⟫", re.S)
NB_NAME = {"en": "NOKTA_AI_Workshop_EN.ipynb", "tr": "NOKTA_AI_Workshop_TR.ipynb"}

# Turkish docstrings and comments of the shared functions
TR_TEXT = {
    '"""Modified z-score: 0.6745 (x - median) / MAD (Leys et al., 2013)."""':
        '"""Değiştirilmiş z-skoru: 0,6745 (x - medyan) / MAD (Leys vd., 2013)."""',
    '"""Robust z-score of the distance from a running median."""':
        '"""Kayan medyandan uzaklığın dayanıklı z-skoru."""',
    '"""Return one boolean column per quality problem (raw data are kept)."""':
        '"""Her kalite sorunu için bir mantıksal sütun döndürür (ham veri korunur)."""',
    "# a real plume lifts every particle size, a glitch lifts only one":
        "# gerçek bir bulut bütün partikül boyutlarını yükseltir, hata yalnızca birini",
    "# spread the flag back over the whole frozen window":
        "# işareti donmuş pencerenin tamamına geri yay",
    '"""Copy of the data with flagged values set to missing (never to zero)."""':
        '"""İşaretli değerleri eksik yapılmış (asla sıfır değil) veri kopyası."""',
    '"""Offset of each station from the mean of the three stations."""':
        '"""Her istasyonun üç istasyonun ortalamasından sapması."""',
    '"""Growth factor C of particle mass with humidity (Crilley et al., 2018)."""':
        '"""Partikül kütlesinin nemle büyüme çarpanı C (Crilley vd., 2018)."""',
    '"""Median of every channel for each minute of each visit."""':
        '"""Her ziyaretin her dakikası için bütün kanalların medyanı."""',
    '"""Dew point (deg C) from the Magnus form (Alduchov & Eskridge, 1996)."""':
        '"""Magnus biçiminden çiy noktası, °C (Alduchov ve Eskridge, 1996)."""',
    '"""Round 1, Round 2, their mean and the difference from the reference."""':
        '"""1. tur, 2. tur, ortalamaları ve referanstan fark."""',
    '"""List every number of a text and whether the fact table supports it."""':
        '"""Metindeki sayıları ve tablonun onları destekleyip desteklemediğini verir."""',
}


def wrap_text(t, width=68):
    """Write a long string as several quoted pieces, one per line."""
    words, lines, cur = t.split(" "), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur + " ")
            cur = w
        else:
            cur = (cur + " " + w) if cur else w
    lines.append(cur)
    return "\n        ".join(repr(x) for x in lines)


def wrap_list(items, indent=4, width=78):
    """Write a list literal over several lines of at most `width` characters."""
    lines, cur = [], "["
    for i, it in enumerate(items):
        piece = repr(it) + (", " if i < len(items) - 1 else "]")
        if len(cur) + len(piece) > width:
            lines.append(cur.rstrip())
            cur = " " * indent + piece
        else:
            cur += piece
    lines.append(cur)
    return "\n".join(lines)


def src(*funcs):
    return "\n\n".join(inspect.getsource(f).rstrip() for f in funcs)


def pick(text, lang):
    out = TOKEN.sub(lambda m: m.group(1) if lang == "en" else m.group(2), text)
    if lang == "tr":
        for a, b in TR_TEXT.items():
            out = out.replace(a, b)
        out = out.replace('"Exercise ', '"Alıştırma ').replace("'Exercise ", "'Alıştırma ")
    return out


IDENT = """<div align="center">

# ⟪NOKTA Workshop: AI-Based Environmental Data Analysis and Interpretation‖NOKTA Atölyesi: Yapay Zekâ ile Çevresel Veri Analizi ve Yorumlama⟫

**⟪Colab notebook of the two-hour workshop‖İki saatlik atölyenin Colab defteri⟫** · NOKTA, ⟪Objective Measurement, Participation, Monitoring and Action Network‖Nesnel Ölçüm, Katılım, Takip ve Aksiyon Ağı⟫ · ÜNİDES 2026

**Prof. Dr. Utku Köse**<br>
⟪Süleyman Demirel University, Isparta, Türkiye · AI Application and Research Center (YAZEM)‖Süleyman Demirel Üniversitesi, Isparta · Yapay Zekâ Uygulama ve Araştırma Merkezi (YAZEM)⟫<br>
University of North Dakota · Universidad Panamericana · Vel Tech University

[⟪Workshop site‖Atölye sitesi⟫](""" + SITE + """⟪‖tr/⟫) · [GitHub](https://github.com/""" + OWNER + "/" + REPO + """) · [ORCID 0000-0002-9652-6415](https://orcid.org/0000-0002-9652-6415) · [utkukose.com](https://www.utkukose.com)

*⟪This workshop is updated in line with current developments in the field. First version: November 2026.‖Bu atölye alandaki güncel gelişmelere göre güncellenmektedir. İlk sürüm: Kasım 2026.⟫*

</div>"""

SIGNATURE = """<div align="center">

---

**Prof. Dr. Utku Köse**<br>
Süleyman Demirel University · University of North Dakota · Universidad Panamericana · Vel Tech University<br>
[utkukose.com](https://www.utkukose.com) · [ORCID 0000-0002-9652-6415](https://orcid.org/0000-0002-9652-6415) · [github.com/utkukose](https://github.com/utkukose)

<sub>⟪NOKTA workshop · ÜNİDES 2026 · First version: November 2026 · Content CC BY 4.0, code MIT · The data are synthetic.‖NOKTA atölyesi · ÜNİDES 2026 · İlk sürüm: Kasım 2026 · İçerik CC BY 4.0, kod MIT · Veriler sentetiktir.⟫</sub>

</div>"""


def cells(expected):
    C = []
    md = lambda t, cid=None: C.append(("md", t, cid))            # noqa: E731
    code = lambda t, cid=None: C.append(("code", t, cid))        # noqa: E731

    md(IDENT, "title")
    md("""## ⟪How to use this notebook‖Bu defter nasıl kullanılır⟫

⟪Save a copy to your Drive first (File, Save a copy in Drive). Run the cells in order with Shift+Enter. Each section belongs to one part of the [workshop site](""" + SITE + """): Section 1 to Part 1, up to Section 5 for Part 5. No installation is needed on Colab.‖Önce Drive'ınıza bir kopya kaydedin (Dosya, Drive'a kopya kaydet). Hücreleri Shift+Enter ile sırayla çalıştırın. Her bölüm [atölye sitesindeki](""" + SITE + """tr/) aynı numaralı bölüme karşılık gelir: 1. Bölümden 5. Bölüme kadar. Colab'da herhangi bir kurulum gerekmez.⟫

- ⟪**Python note** cells explain a piece of the Python language where it first appears.‖**Python notu** hücreleri Python dilinin bir parçasını ilk kullanıldığı yerde açıklar.⟫
- ⟪**Exercises** give instant feedback with `check(...)`. Reference solutions sit in folded cells and should be opened only after trying.‖**Alıştırmalar** `check(...)` ile anında geri bildirim verir. Örnek çözümler katlanmış hücrelerdedir ve ancak denedikten sonra açılmalıdır.⟫
- ⟪**Observe and reflect** asks open questions about an output and has no solution cell.‖**Gözlemle ve düşün** bir çıktı hakkında açık uçlu sorular sorar ve çözüm hücresi içermez.⟫
- ⟪The data are synthetic and follow the NOKTA protocol. Section 0 shows how to load real NOKTA files instead.‖Veriler sentetiktir ve NOKTA protokolünü izler. 0. Bölüm bunun yerine gerçek NOKTA dosyalarının nasıl yükleneceğini gösterir.⟫""", "howto")

    # ------------------------------------------------------------------ 0
    md("""## 0. ⟪Setup and data‖Kurulum ve veri⟫

⟪The first cell loads the libraries and the helper `check`. The second cell reads four files: The readings (one row every 10 seconds), the field forms (one row per visit), the side-by-side test of the three stations and, for the synthetic data only, a list of the problems that were planted on purpose.‖İlk hücre kütüphaneleri ve `check` yardımcısını yükler. İkinci hücre dört dosya okur: Ölçümler (her 10 saniyede bir satır), saha formları (her ziyaret için bir satır), üç istasyonun yan yana testi ve yalnızca sentetik veride bilerek yerleştirilmiş sorunların listesi.⟫

⟪**Your own NOKTA data.** Set `DATA_SOURCE = "own"` and upload your CSV files with the columns of `data/nokta_template.csv` (Files panel on the left). If your logger uses other column names, fill `COLUMN_MAP`. Everything after this cell then runs on your data.‖**Kendi NOKTA veriniz.** `DATA_SOURCE = "own"` yapın ve `data/nokta_template.csv` sütunlarına sahip CSV dosyalarınızı yükleyin (soldaki Dosyalar paneli). Kayıt cihazınız başka sütun adları kullanıyorsa `COLUMN_MAP` sözlüğünü doldurun. Bu hücreden sonraki her şey sizin verinizle çalışır.⟫""", "sec-0")
    code("""import json, re, urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Markdown

RANDOM_STATE = 2026
plt.rcParams.update({"font.family": "DejaVu Sans", "figure.dpi": 110,
                     "axes.spines.top": False, "axes.spines.right": False})
pd.set_option("display.width", 140)
try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:                      # ⟪matplotlib is used instead‖yerine matplotlib kullanılır⟫
    HAS_PLOTLY = False

TYPE_ORDER = ["shaded", "traffic", "reference", "sunny_hard", "crowded", "green"]
TYPE_COLOR = {"shaded": "#2a78d6", "traffic": "#eb6834", "reference": "#1baf7a",
              "sunny_hard": "#eda100", "crowded": "#e87ba4", "green": "#008300"}
TYPE_NAME = {"shaded": "⟪Shaded‖Gölgeli⟫", "traffic": "⟪Traffic‖Trafik⟫",
             "reference": "⟪Reference‖Referans⟫", "sunny_hard": "⟪Sunny hard‖Güneşli sert⟫",
             "crowded": "⟪Busy‖Yoğun⟫", "green": "⟪Green‖Yeşil⟫"}


def check(name, value, tol=0.01):
    \"\"\"⟪Compare an exercise answer with the expected answer.‖Bir alıştırma cevabını beklenen cevapla karşılaştırır.⟫\"\"\"
    exp = EXPECTED.get(name)
    if value is None:
        print(f"{name}: ⟪no answer yet‖henüz cevap yok⟫")
        return False
    if isinstance(exp, str):
        ok = str(value).strip().lower() == exp
    else:
        ok = abs(float(value) - exp) <= tol
    print(f"{name}: " + ("⟪correct‖doğru⟫ ✓" if ok else "⟪not yet, try again‖henüz değil, yeniden deneyin⟫"))
    return ok

print("⟪Ready. Plotly for 3D plots:‖Hazır. 3B grafikler için Plotly:⟫", HAS_PLOTLY)""", "setup")
    code("#@title ⟪Expected answers of the exercises (run this cell; open it only after trying the exercises)‖Alıştırmaların beklenen cevapları (bu hücreyi çalıştırın; ancak alıştırmaları denedikten sonra açın)⟫\n"
         "EXPECTED = {\n" + "".join(f"    {k!r}: {v!r},\n" for k, v in expected.items()) + "}", "expected")
    code("""DATA_SOURCE = "synthetic"        # ⟪"synthetic" or "own"‖"synthetic" ya da "own"⟫
REPO_RAW = ("https://raw.githubusercontent.com/""" + OWNER + """/"
            \"""" + REPO + """/main/data/")
FILES = {"readings": "nokta_synthetic.csv",
         "forms": "nokta_field_forms_synthetic.csv",
         "coloc": "nokta_colocation_synthetic.csv",
         "truth": "nokta_synthetic_qc_truth.csv"}
OWN_FILES = {"readings": "my_readings.csv", "forms": "my_field_forms.csv",
             "coloc": "my_colocation.csv"}
COLUMN_MAP = {}                    # ⟪e.g. {"Temp": "temperature_c"}‖ör. {"Temp": "temperature_c"}⟫


def fetch(name):
    \"\"\"⟪Local copy if present, otherwise a download from GitHub.‖Varsa yerel kopya, yoksa GitHub'dan indirme.⟫\"\"\"
    for folder in (Path("data"), Path("../data"), Path("workshop_data")):
        if (folder / name).exists():
            return folder / name
    Path("workshop_data").mkdir(exist_ok=True)
    target = Path("workshop_data") / name
    urllib.request.urlretrieve(REPO_RAW + name, target)
    return target


if DATA_SOURCE == "own":
    paths = {k: Path(v) for k, v in OWN_FILES.items()}
else:
    paths = {k: fetch(v) for k, v in FILES.items()}
print({k: str(v) for k, v in paths.items()})""", "data-source")

    # ------------------------------------------------------------------ Python step
    md("""## ⟪Python step: Five ideas for reading the code‖Python adımı: Kodu okumak için beş fikir⟫

⟪Participants without Python can read this step in five minutes and skip it in the live session.‖Python bilmeyen katılımcılar bu adımı beş dakikada okuyabilir ve canlı oturumda atlayabilir.⟫

1. ⟪**Variables** keep a value under a name: `rh = 43.0`.‖**Değişkenler** bir değeri bir adla saklar: `rh = 43.0`.⟫
2. ⟪**Lists** keep several values in order: `pm = [14.2, 15.0, 13.8]`, and `pm[0]` is the first one.‖**Listeler** birkaç değeri sırayla tutar: `pm = [14.2, 15.0, 13.8]` ve `pm[0]` ilk değerdir.⟫
3. ⟪**Dictionaries** link names to values: `{"P1": "shaded"}`.‖**Sözlükler** adları değerlere bağlar: `{"P1": "shaded"}`.⟫
4. ⟪**Functions** package a calculation: `def dew_point(t, rh): ...` is run with `dew_point(13.3, 43)`.‖**Fonksiyonlar** bir hesabı paketler: `def dew_point(t, rh): ...` tanımı `dew_point(13.3, 43)` ile çalıştırılır.⟫
5. ⟪**pandas tables (DataFrames)** hold the NOKTA readings: One row per reading, one column per channel. `df["pm25_ugm3"]` is one column, `df.groupby("point_type")` splits the rows by point.‖**pandas tabloları (DataFrame)** NOKTA ölçümlerini tutar: Her ölçüm için bir satır, her kanal için bir sütun. `df["pm25_ugm3"]` bir sütundur, `df.groupby("point_type")` satırları noktalara göre ayırır.⟫""", "python-step")
    code("""# ⟪Python practice: a small example for learning the language‖Python alıştırması: Dili öğrenmek için küçük bir örnek⟫
pm = [14.2, 15.0, 13.8, 14.6, 97.3, 15.1, 14.4]      # ⟪a list of PM2.5 readings‖PM2,5 ölçümlerinden bir liste⟫
print("⟪number of readings:‖ölçüm sayısı:⟫", len(pm))
print("⟪mean:‖ortalama:⟫", round(sum(pm) / len(pm), 2))
print("⟪median:‖medyan:⟫", sorted(pm)[len(pm) // 2])
point = {"id": "P2", "type": "traffic", "vehicles_15min": 104}
print(f"{point['id']}: {point['type']},",
      point["vehicles_15min"], "⟪vehicles in 15 minutes‖araç, 15 dakikada⟫")""", "py-1")
    md("""⟪**Python note.** `f"..."` is a formatted text: Values inside `{ }` are written into it. `round(x, 2)` keeps two decimals, `sorted(...)` returns a sorted copy and `//` divides without the remainder.‖**Python notu.** `f"..."` biçimlendirilmiş bir metindir: `{ }` içindeki değerler metne yazılır. `round(x, 2)` iki ondalık basamak bırakır, `sorted(...)` sıralanmış bir kopya döndürür ve `//` kalansız böler.⟫""", "py-note-1")

    # ------------------------------------------------------------------ 1
    md("""## 1. ⟪Measure: The campus as data‖Ölç: Veri olarak kampüs⟫

*⟪Workshop site: [Part 1](""" + SITE + """part1.html)‖Atölye sitesi: [1. Bölüm](""" + SITE + """tr/part1.html)⟫*

### 1.1 ⟪Load and look‖Yükle ve bak⟫""", "sec-1")
    code(src(core.load_readings) + """


CHANNELS = """ + wrap_list(core.CHANNELS) + """
PM = """ + repr(core.PM) + """
LUX_MAX = 65535

df = load_readings(paths["readings"])
df = df.rename(columns=COLUMN_MAP)
forms = pd.read_csv(paths["forms"])
coloc = pd.read_csv(paths["coloc"])
print(df.shape[0], "⟪readings,‖ölçüm,⟫", forms.shape[0], "⟪visits,‖ziyaret,⟫",
      df["campus"].nunique(), "⟪campuses‖kampüs⟫")
display(df.head(3))
display(df.groupby(["campus", "round"])["point_id"].nunique().unstack())""", "s1-load")
    md("""⟪**Python note.** `df.groupby([...])[col].nunique()` counts the different values of a column in each group, and `.unstack()` turns the inner group into columns.‖**Python notu.** `df.groupby([...])[col].nunique()` her gruptaki farklı değerleri sayar, `.unstack()` ise iç grubu sütunlara çevirir.⟫""", "py-note-2")
    code("""visit = df[df["visit"] == "A-R1-P2"]     # ⟪Campus A, Round 1, near traffic‖Kampüs A, 1. tur, trafiğe yakın⟫
fig, axes = plt.subplots(1, 3, figsize=(13, 3.2))
for ax, ch in zip(axes, ["temperature_c", "pm25_ugm3", "co2_ppm"]):
    ax.plot(visit["seconds_since_arrival"] / 60, visit[ch], lw=1.4, color="#0E7A5F")
    ax.axvspan(0, 2, color="#eda100", alpha=0.15)
    ax.set_title(ch); ax.set_xlabel("⟪minutes since arrival‖varıştan sonraki dakika⟫")
plt.tight_layout(); plt.show()""", "s1-plot")

    md("""### 1.2 ⟪Quality flags‖Kalite işaretleri⟫

⟪Raw data are never changed. The functions below add one true or false column per problem: Warm-up after a move, logger gaps, a light sensor at its limit, humidity above 85 %, single-channel glitches, CO₂ out of range and a frozen CO₂ sensor. The spike test uses the modified z-score of Part 1:‖Ham veri asla değiştirilmez. Aşağıdaki fonksiyonlar her sorun için doğru ya da yanlış değerli bir sütun ekler: Taşıma sonrası ısınma, kayıt boşlukları, sınırına ulaşmış ışık sensörü, %85 üzerindeki nem, tek kanallı hatalar, aralık dışı CO₂ ve donmuş CO₂ sensörü. Sıçrama testi 1. Bölümdeki değiştirilmiş z-skorunu kullanır:⟫

$$M_i = \\frac{0.6745\\,(x_i - \\tilde{x})}{\\mathrm{MAD}}$$

*⟪From the formulas to the code: `robust_z` is M, `spike_scores` applies it to the distance from a running median of five readings.‖Formüllerden koda: `robust_z` M'dir, `spike_scores` bunu beş ölçümlük kayan medyandan uzaklığa uygular.⟫*""", "s1-qc-md")
    code(src(core.robust_z, core.spike_scores, core.flag_quality, core.clean_readings) + """


flags = flag_quality(df)
display(flags.sum().rename("⟪flagged readings‖işaretli ölçüm⟫").to_frame().T)""", "s1-qc")
    code("""if "truth" in paths:     # ⟪only the synthetic data have planted problems‖yalnızca sentetik veride bulunur⟫
    truth = pd.read_csv(paths["truth"])["qc_truth"].to_numpy()
    pairs = {"warmup": "warmup", "spike_pm25": "spike_pm25_ugm3",
             "spike_pm10": "spike_pm10_ugm3", "spike_co2": "spike_co2_ppm",
             "flatline_co2": "flatline_co2", "gap": "gap"}
    rows = [dict(problem=k, planted=int((truth == k).sum()),
                 flagged=int(flags[v].sum()),
                 caught=int(((truth == k) & flags[v].to_numpy()).sum()))
            for k, v in pairs.items()]
    display(pd.DataFrame(rows))
v = df["visit"] == "B-R1-P1"
plt.figure(figsize=(9, 3))
plt.plot(df.loc[v, "seconds_since_arrival"] / 60, df.loc[v, "co2_ppm"],
         color="#0E7A5F")
bad = v & (flags["flatline_co2"] | flags["spike_co2_ppm"])
plt.scatter(df.loc[bad, "seconds_since_arrival"] / 60, df.loc[bad, "co2_ppm"],
            facecolors="none", edgecolors="#B3261E", s=50, label="⟪flagged‖işaretli⟫")
plt.axvspan(0, 2, color="#eda100", alpha=0.15, label="⟪warm-up‖ısınma⟫")
plt.ylabel("CO₂ (ppm)"); plt.xlabel("⟪minutes since arrival‖varıştan sonraki dakika⟫")
plt.legend(); plt.show()""", "s1-qc-score")
    md("""### ⟪Exercise 1.A‖Alıştırma 1.A⟫

⟪Compute the modified z-score of the reading 97.3 among the seven readings of the worked example with `robust_z`. Store the value in `answer`.‖Çözümlü örnekteki yedi ölçüm arasında 97,3 değerinin değiştirilmiş z-skorunu `robust_z` ile hesaplayın. Değeri `answer` değişkenine yazın.⟫""", "ex-1a-md")
    code("""readings = np.array([14.2, 15.0, 13.8, 14.6, 97.3, 15.1, 14.4])
answer = None   # your answer
check("Exercise 1.A", answer)""", "ex-1a")
    code("""#@title ⟪Reference solution (run this cell; open it only after trying)‖Örnek çözüm (bu hücreyi çalıştırın; ancak denedikten sonra açın)⟫
answer = robust_z(readings)[4]
print(round(answer, 2))
check("Exercise 1.A", answer)""", "ex-1a-sol")

    md("""### 1.3 ⟪A second opinion from AI: Isolation Forest‖YZ'den ikinci görüş: Isolation Forest⟫

⟪Rules catch the problems that someone thought of. An Isolation Forest looks for readings that are easy to separate from the rest in all channels at once [Liu et al., 2008]. Its flags are a list to review with the field notes, not a list to delete.‖Kurallar, birinin önceden düşündüğü sorunları yakalar. Isolation Forest ise bütün kanallarda aynı anda geri kalanlardan kolayca ayrılan ölçümleri arar [Liu vd., 2008]. İşaretleri silinecek değil, saha notlarıyla gözden geçirilecek bir listedir.⟫""", "s1-if-md")
    code("""from sklearn.ensemble import IsolationForest

X_if = df[CHANNELS].copy()
X_if = (X_if - X_if.groupby(df["visit"]).transform("median")).fillna(0)
iso = IsolationForest(n_estimators=200, contamination=0.02,
                      random_state=RANDOM_STATE).fit(X_if)
df["if_flag"] = iso.predict(X_if) == -1
rule_any = flags.drop(columns=["high_rh"]).any(axis=1)
print("⟪Isolation Forest flags:‖Isolation Forest işaretleri:⟫", int(df["if_flag"].sum()))
print("⟪of these, also flagged by a rule:‖bunlardan bir kuralın da işaretledikleri:⟫",
      int((df["if_flag"] & rule_any).sum()))
display(df.loc[df["if_flag"] & ~rule_any,
               ["visit", "seconds_since_arrival", "pm25_ugm3", "co2_ppm"]].head(8))""", "s1-if")
    md("""⟪**Missing is not zero.** One logger restart left six empty readings. Compare the mean when they are skipped with the mean when they are written as zero.‖**Eksik değer sıfır değildir.** Kayıt cihazının yeniden başlaması altı boş ölçüm bıraktı. Boş ölçümler atlandığında ve sıfır yazıldığında ortalamaları karşılaştırın.⟫""", "s1-gap-md")
    code("""gap = df[df["visit"] == "A-R2-P5"]["temperature_c"].iloc[30:52]
print("⟪skipped:‖atlanınca:⟫", round(gap.mean(), 2), "°C   ⟪written as zero:‖sıfır yazılınca:⟫",
      round(gap.fillna(0).mean(), 2), "°C")""", "s1-gap")

    md("""### 1.4 ⟪Three stations, one story‖Üç istasyon, tek hikâye⟫

$$o_s = \\frac{1}{T}\\sum_{t=1}^{T}\\bigl(x_s(t) - \\bar{x}(t)\\bigr)$$

*⟪From the formulas to the code: `colocation_offsets` computes o for temperature, humidity and CO₂ and a ratio for particles. `apply_offsets` then subtracts or divides.‖Formüllerden koda: `colocation_offsets` sıcaklık, nem ve CO₂ için o değerini, partiküller için bir oranı hesaplar. `apply_offsets` çıkarır ya da böler.⟫*""", "s1-coloc-md")
    code(src(core.colocation_offsets, core.apply_offsets) + """


offsets = colocation_offsets(coloc)
display(offsets.round(3))""", "s1-coloc")

    md("""### 1.5 ⟪Humid air and the particle counter‖Nemli hava ve partikül sayacı⟫

$$C(a_w) = 1 + \\frac{\\kappa\\,\\rho_w/\\rho_p}{-1 + 1/a_w}, \\qquad a_w = \\mathrm{RH}/100$$

⟪The correction of Crilley et al. (2018) uses κ = 0.3 and ρ<sub>p</sub> = 1.65 g/cm³. A real study estimates κ for the local air against a reference instrument.‖Crilley vd. (2018) düzeltmesi κ = 0,3 ve ρ<sub>p</sub> = 1,65 g/cm³ kullanır. Gerçek bir çalışma κ değerini yerel hava için bir referans cihazla kestirir.⟫""", "s1-hum-md")
    code(src(core.humidity_factor, core.correct_pm) + """


for rh in (50, 70, 85, 90):
    print(f"RH {rh} %  ->  C = {humidity_factor(rh):.2f}")""", "s1-hum")

    md("""### 1.6 ⟪The table of clean minutes‖Temiz dakika tablosu⟫

⟪Flagged values become missing, the station offsets are removed, particles are corrected for humidity and every visit is summarized minute by minute. Parts 2 to 4 start from this table.‖İşaretli değerler eksik yapılır, istasyon sapmaları giderilir, partiküller neme göre düzeltilir ve her ziyaret dakika dakika özetlenir. 2-4. kısımlar bu tablodan başlar.⟫""", "s1-min-md")
    code(src(core.minute_table) + """


clean = clean_readings(df, flags)
adjusted_raw_pm = apply_offsets(clean, offsets)
adjusted = correct_pm(adjusted_raw_pm)
minutes = minute_table(adjusted)
minutes_raw_pm = minute_table(adjusted_raw_pm)
minutes.to_csv("nokta_clean_minutes.csv", index=False)
print(len(minutes), "⟪clean minutes saved to nokta_clean_minutes.csv‖temiz dakika nokta_clean_minutes.csv dosyasına kaydedildi⟫")
c2 = (minutes.campus == "C") & (minutes["round"] == 2)
display(pd.DataFrame({
    "⟪raw PM2.5‖ham PM2,5⟫": minutes_raw_pm[c2].groupby("point_type")["pm25_ugm3"].median(),
    "⟪corrected‖düzeltilmiş⟫": minutes[c2].groupby("point_type")["pm25_ugm3"].median(),
    "RH %": minutes[c2].groupby("point_type")["rel_humidity_pct"].median(),
}).round(2))""", "s1-min")
    md("""⟪**Observe and reflect.** Which of the flags would you check first with the field notes, and why? Which problems could a rule never find, but a team member at the point would notice at once?‖**Gözlemle ve düşün.** Hangi işaretleri önce saha notlarıyla kontrol ederdiniz ve neden? Hangi sorunları bir kural asla bulamaz, ama noktadaki bir ekip üyesi hemen fark eder?⟫""", "s1-obs")

    # ------------------------------------------------------------------ 2
    md("""## 2. ⟪Analyze: Fair comparisons‖Analiz et: Adil karşılaştırma⟫

*⟪Workshop site: [Part 2](""" + SITE + """part2.html)‖Atölye sitesi: [2. Bölüm](""" + SITE + """tr/part2.html)⟫*

### 2.1 ⟪The clock behind every point‖Her noktanın arkasındaki saat⟫""", "sec-2")
    code(src(core.visit_table) + """


visits = visit_table(minutes)
a = visits[visits.campus == "A"]
fig, ax = plt.subplots(figsize=(8, 3.6))
for rd, style in ((1, "-"), (2, "--")):
    r = a[a["round"] == rd].sort_values("hour")
    ax.plot(r["hour"], r["temperature_c"], style, color="gray", lw=1)
    colors = [TYPE_COLOR[t] for t in r.point_type]
    ax.scatter(r["hour"], r["temperature_c"], c=colors, s=70, zorder=3)
ax.set_xlabel("⟪clock time (hours)‖saat⟫"); ax.set_ylabel("°C")
ax.set_title("⟪Campus A: Round 1 (solid) and Round 2 (dashed)‖Kampüs A: 1. tur (düz) ve 2. tur (kesikli)⟫")
plt.show()""", "s2-drift")
    md("""### 2.2 ⟪The two-round mean and the reference point‖İki tur ortalaması ve referans noktası⟫

$$\\bar{x}_p = \\frac{x_{p,1} + x_{p,2}}{2}, \\qquad \\Delta_p = \\bar{x}_p - \\bar{x}_{\\text{ref}}$$""", "s2-fair-md")
    code(src(core.fair_table) + """


fair_t = fair_table(visits, "temperature_c")
display(fair_t[fair_t.campus == "A"].round(2))
fair_pm = fair_table(visits, "pm25_ugm3")
pivot = fair_pm.pivot(index="point_type", columns="campus", values="minus_reference")
pivot.loc[TYPE_ORDER].plot.barh(figsize=(7, 3.6),
                                color=["#2a78d6", "#eb6834", "#1baf7a"])
plt.axvline(0, color="black", lw=0.8)
plt.xlabel("⟪PM2.5 minus the reference point (µg/m³)‖PM2,5 eksi referans noktası (µg/m³)⟫")
plt.show()""", "s2-fair")
    md("""### ⟪Exercise 2.A‖Alıştırma 2.A⟫

⟪Using `fair_t`, find the difference of the green area from the reference point on Campus A (°C).‖`fair_t` tablosunu kullanarak Kampüs A'da yeşil alanın referans noktasından farkını bulun (°C).⟫""", "ex-2a-md")
    code("""answer = None   # your answer
check("Exercise 2.A", answer)""", "ex-2a")
    code("""#@title ⟪Reference solution (run this cell; open it only after trying)‖Örnek çözüm (bu hücreyi çalıştırın; ancak denedikten sonra açın)⟫
row = fair_t[(fair_t.campus == "A") & (fair_t.point_type == "green")]
answer = row["minus_reference"].iloc[0]
print(round(answer, 2))
check("Exercise 2.A", answer)""", "ex-2a-sol")
    md("""### 2.3 ⟪Typical values‖Tipik değerler⟫""", "s2-box-md")
    code(src(core.add_anomalies) + """


anom = add_anomalies(minutes)
fig, ax = plt.subplots(figsize=(9, 3.6))
data = [anom.loc[anom.point_type == t, "pm25_anomaly"].dropna() for t in TYPE_ORDER]
bp = ax.boxplot(data, patch_artist=True, showmeans=True)
for patch, t in zip(bp["boxes"], TYPE_ORDER):
    patch.set_facecolor(TYPE_COLOR[t])
ax.set_xticks(range(1, 7), [TYPE_NAME[t] for t in TYPE_ORDER])
ax.set_ylabel("⟪PM2.5 minus campus-round median (µg/m³)‖PM2,5 eksi kampüs-tur medyanı (µg/m³)⟫")
plt.show()
display(anom.groupby("point_type")["pm25_anomaly"].agg(["median", "mean"]).round(2))""", "s2-box")
    md("""### 2.4 ⟪Related or caused?‖İlişki mi, neden mi?⟫""", "s2-corr-md")
    code(src(core.pearson_r) + """


r_all = pearson_r(minutes.temperature_c, minutes.pressure_hpa)
print("⟪all minutes:‖bütün dakikalar:⟫", round(r_all, 3))
for (c, rd), g in minutes.groupby(["campus", "round"]):
    print(f"{c}{rd}:", round(pearson_r(g.temperature_c, g.pressure_hpa), 3))
corr = minutes[CHANNELS].corr()
plt.figure(figsize=(6.5, 5.2))
plt.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
plt.xticks(range(10), CHANNELS, rotation=60, ha="right")
plt.yticks(range(10), CHANNELS)
plt.colorbar(label="r"); plt.title("⟪Correlation of the ten channels‖On kanalın korelasyonu⟫")
plt.show()""", "s2-corr")
    md("""### 2.5 ⟪Dew point‖Çiy noktası⟫

$$\\gamma = \\ln\\frac{\\mathrm{RH}}{100} + \\frac{a\\,T}{b + T}, \\qquad T_d = \\frac{b\\,\\gamma}{a - \\gamma}, \\quad a = 17.625,\\ b = 243.04\\ ^\\circ\\mathrm{C}$$""", "s2-dew-md")
    code(src(core.dew_point) + """


minutes["dew_point_c"] = dew_point(minutes.temperature_c, minutes.rel_humidity_pct)
display(minutes.pivot_table(index=["campus", "round"], columns="point_type",
                            values="dew_point_c", aggfunc="median").round(1))""", "s2-dew")
    md("""### ⟪Exercise 2.B‖Alıştırma 2.B⟫

⟪What is the dew point of air at 20 °C and 50 % relative humidity? Use `dew_point`.‖20 °C sıcaklık ve %50 bağıl nemdeki havanın çiy noktası nedir? `dew_point` fonksiyonunu kullanın.⟫""", "ex-2b-md")
    code("""answer = None   # your answer
check("Exercise 2.B", answer)""", "ex-2b")
    code("""#@title ⟪Reference solution (run this cell; open it only after trying)‖Örnek çözüm (bu hücreyi çalıştırın; ancak denedikten sonra açın)⟫
answer = dew_point(20.0, 50.0)
print(round(answer, 2))
check("Exercise 2.B", answer)""", "ex-2b-sol")
    md("""⟪**Observe and reflect.** On which campus and round is the dew point highest, and what does that say about the air of that morning? Why does the green area sit slightly higher?‖**Gözlemle ve düşün.** Çiy noktası hangi kampüs ve turda en yüksek ve bu, o sabahın havası hakkında ne söyler? Yeşil alan neden biraz daha yüksektir?⟫""", "s2-obs")

    # ------------------------------------------------------------------ 3
    md("""## 3. ⟪Discover: AI finds patterns‖Keşfet: YZ örüntü bulur⟫

*⟪Workshop site: [Part 3](""" + SITE + """part3.html)‖Atölye sitesi: [3. Bölüm](""" + SITE + """tr/part3.html)⟫*

### 3.1 ⟪Standardize‖Standartlaştır⟫

$$z_{ij} = \\frac{x_{ij} - \\mu_j}{\\sigma_j}$$""", "sec-3")
    code(src(core.standardize) + """


CLUSTER_FEATURES = """ + repr(core.CLUSTER_FEATURES) + """
X = anom[CLUSTER_FEATURES].to_numpy()
Z, mu, sd = standardize(X)
print("μ =", mu.round(3), "  σ =", sd.round(3))""", "s3-std")
    md("""### 3.2 ⟪k-means with k = 4‖k = 4 ile k-ortalamalar⟫""", "s3-km-md")
    code("""from sklearn.cluster import KMeans

km = KMeans(n_clusters=4, n_init=10, random_state=RANDOM_STATE).fit(Z)
order = np.argsort(km.cluster_centers_[:, 0])          # ⟪coolest group first‖en serin grup önce⟫
rename = {old: new + 1 for new, old in enumerate(order)}
anom["group"] = pd.Series(km.labels_).map(rename).to_numpy()
centers = pd.DataFrame(km.cluster_centers_[order] * sd + mu,
                       columns=CLUSTER_FEATURES, index=[1, 2, 3, 4]).round(2)
display(centers)
display(pd.crosstab(anom["group"], anom["point_type"])[TYPE_ORDER])""", "s3-km")
    code("""if HAS_PLOTLY:
    fig = px.scatter_3d(anom, x="temp_anomaly", y="log10_lux", z="pm25_anomaly",
                        color=anom["group"].astype(str), opacity=0.75,
                        hover_data=["campus", "round", "point_type"],
                        title="⟪k-means groups of the clean minutes‖Temiz dakikaların k-ortalamalar grupları⟫")
    fig.update_traces(marker_size=3)
    fig.show()
else:
    ax = plt.figure(figsize=(6, 5)).add_subplot(projection="3d")
    ax.scatter(anom.temp_anomaly, anom.log10_lux, anom.pm25_anomaly,
               c=anom.group, s=8)
    ax.set_xlabel("ΔT"); ax.set_ylabel("log10 lux"); ax.set_zlabel("ΔPM2.5")
    plt.show()""", "s3-3d")
    md("""### 3.3 ⟪How many groups?‖Kaç grup?⟫""", "s3-k-md")
    code("""from sklearn.metrics import silhouette_score

rows = []
for k in range(2, 7):
    m = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE).fit(Z)
    rows.append(dict(k=k, J=round(m.inertia_, 1),
                     silhouette=round(silhouette_score(Z, m.labels_), 3)))
scores = pd.DataFrame(rows)
display(scores)""", "s3-k")
    md("""### ⟪Exercise 3.A‖Alıştırma 3.A⟫

⟪Which k has the highest silhouette score in `scores`?‖`scores` tablosunda hangi k değeri en yüksek siluet skoruna sahip?⟫""", "ex-3a-md")
    code("""answer = None   # your answer
check("Exercise 3.A", answer)""", "ex-3a")
    code("""#@title ⟪Reference solution (run this cell; open it only after trying)‖Örnek çözüm (bu hücreyi çalıştırın; ancak denedikten sonra açın)⟫
answer = int(scores.loc[scores.silhouette.idxmax(), "k"])
print(answer)
check("Exercise 3.A", answer)""", "ex-3a-sol")
    md("""### 3.4 ⟪Principal component analysis‖Temel bileşen analizi⟫""", "s3-pca-md")
    code("""from sklearn.decomposition import PCA

feats = ["temp_anomaly", "rel_humidity_pct", "pm25_anomaly", "co2_anomaly",
         "log10_lux", "uva_wm2"]
P = anom[feats].copy()
# ⟪a missing minute is placed at the median‖eksik dakika medyana yerleştirilir⟫
P["co2_anomaly"] = P["co2_anomaly"].fillna(0.0)
Zp, _, _ = standardize(P.to_numpy())
pca = PCA(n_components=3, random_state=RANDOM_STATE).fit(Zp)
print("⟪share of variation:‖değişimin payı:⟫", pca.explained_variance_ratio_.round(3))
loadings = pd.DataFrame(pca.components_, columns=feats, index=["PC1", "PC2", "PC3"])
display(loadings.round(2))
S = pca.transform(Zp)
if HAS_PLOTLY:
    fig = px.scatter_3d(x=S[:, 0], y=S[:, 1], z=S[:, 2], color=anom["point_type"],
                        color_discrete_map=TYPE_COLOR,
                        labels={"x": "PC1", "y": "PC2", "z": "PC3"})
    fig.update_traces(marker_size=3)
    fig.show()""", "s3-pca")
    md("""⟪**Observe and reflect.** Which group mixes several point types, and what do those minutes have in common? Would you trust the same four groups on a cloudy day?‖**Gözlemle ve düşün.** Hangi grup birkaç nokta türünü karıştırıyor ve bu dakikaların ortak yanı ne? Aynı dört gruba bulutlu bir günde de güvenir miydiniz?⟫""", "s3-obs")

    # ------------------------------------------------------------------ 4
    md("""## 4. ⟪Explain: Why is it high here?‖Açıkla: Burada neden yüksek?⟫

*⟪Workshop site: [Part 4](""" + SITE + """part4.html)‖Atölye sitesi: [4. Bölüm](""" + SITE + """tr/part4.html)⟫*

### 4.1 ⟪The model table‖Model tablosu⟫""", "sec-4")
    code(src(core.model_table) + """


MODEL_FEATURES = """ + wrap_list(core.MODEL_FEATURES, width=64) + """
table = model_table(minutes, forms).dropna(subset=MODEL_FEATURES + ["pm25_ugm3"])
Xm = table[MODEL_FEATURES].to_numpy()
y = table["pm25_ugm3"].to_numpy()
groups = (table.campus + table.point_id).to_numpy()
print(len(y), "⟪minutes from‖dakika,⟫", len(set(groups)), "⟪measurement points‖ölçüm noktası⟫")
display(table[MODEL_FEATURES + ["pm25_ugm3"]].head(3))""", "s4-table")
    md("""### 4.2 ⟪Three scores‖Üç skor⟫

$$R^2 = 1 - \\frac{\\sum_i (y_i - \\hat{y}_i)^2}{\\sum_i (y_i - \\bar{y})^2}$$""", "s4-cv-md")
    code("""from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold, LeaveOneGroupOut, cross_val_predict


def make_forest():
    return RandomForestRegressor(n_estimators=40, max_depth=6, min_samples_leaf=5,
                                 random_state=RANDOM_STATE, n_jobs=-1)


forest = make_forest().fit(Xm, y)
p_random = cross_val_predict(make_forest(), Xm, y,
                             cv=KFold(5, shuffle=True, random_state=RANDOM_STATE))
p_group = cross_val_predict(make_forest(), Xm, y, cv=LeaveOneGroupOut(),
                            groups=groups)
scores_cv = pd.Series({"⟪own training minutes‖kendi eğitim dakikaları⟫": r2_score(y, forest.predict(Xm)),
                       "⟪random minutes (5-fold)‖rastgele dakikalar (5 katlı)⟫": r2_score(y, p_random),
                       "⟪leave one point out‖bir noktayı dışarıda bırak⟫": r2_score(y, p_group)}).round(3)
display(scores_cv.to_frame("R²"))""", "s4-cv")
    md("""### 4.3 ⟪Permutation importance‖Permütasyon önemi⟫

⟪Train on two campuses, shuffle one input at a time on the third and measure the drop of R². The three results are averaged.‖İki kampüste eğit, üçüncüsünde girdileri tek tek karıştır ve R² düşüşünü ölç. Üç sonuç ortalanır.⟫""", "s4-imp-md")
    code("""from sklearn.inspection import permutation_importance


def campus_importance(tab, target="pm25_ugm3"):
    X_, y_ = tab[MODEL_FEATURES].to_numpy(), tab[target].to_numpy()
    res = []
    for c in sorted(tab.campus.unique()):
        train = (tab.campus != c).to_numpy()
        m = make_forest().fit(X_[train], y_[train])
        pi = permutation_importance(m, X_[~train], y_[~train], n_repeats=10,
                                    random_state=RANDOM_STATE)
        res.append(pi.importances_mean)
    return pd.Series(np.mean(res, axis=0), index=MODEL_FEATURES).sort_values()


imp = campus_importance(table)
imp.plot.barh(figsize=(6, 3.4), color="#A65400")
plt.xlabel("⟪drop of R² when shuffled‖karıştırıldığında R² düşüşü⟫"); plt.show()""", "s4-imp")
    md("""### ⟪Exercise 4.A‖Alıştırma 4.A⟫

⟪Which input has the largest importance? Write its name as text, for example `"hour"`. The reference solution then repeats the importance for the raw PM2.5 without the humidity correction (`minutes_raw_pm`), so the two columns can be compared.‖Hangi girdinin önemi en büyük? Adını metin olarak yazın, örneğin `"hour"`. Örnek çözüm, önemi nem düzeltmesi yapılmamış ham PM2,5 için (`minutes_raw_pm`) de hesaplar. Böylece iki sütun karşılaştırılabilir.⟫""", "ex-4a-md")
    code("""answer = None   # your answer
check("Exercise 4.A", answer)""", "ex-4a")
    code("""#@title ⟪Reference solution (run this cell; open it only after trying)‖Örnek çözüm (bu hücreyi çalıştırın; ancak denedikten sonra açın)⟫
answer = imp.idxmax()
print(answer)
check("Exercise 4.A", answer)
raw_table = model_table(minutes_raw_pm, forms)
raw_table = raw_table.dropna(subset=MODEL_FEATURES + ["pm25_ugm3"])
both = pd.DataFrame({"⟪corrected‖düzeltilmiş⟫": imp, "⟪raw‖ham⟫": campus_importance(raw_table)})
display(both.round(3))""", "ex-4a-sol")
    md("""### 4.4 ⟪What if?‖Ya şöyle olsaydı?⟫

⟪Move the sliders. The bars show how much the prediction falls when one input goes back to its median.‖Kaydırıcıları hareket ettirin. Çubuklar, bir girdi medyanına döndüğünde tahminin ne kadar düştüğünü gösterir.⟫""", "s4-wi-md")
    code("""import ipywidgets as widgets

med = np.median(Xm, axis=0)
sliders = {f: widgets.FloatSlider(value=float(med[i]), min=float(Xm[:, i].min()),
                                  max=float(Xm[:, i].max()),
                                  step=float((Xm[:, i].max() - Xm[:, i].min()) / 50),
                                  description=f[:18], continuous_update=False)
           for i, f in enumerate(MODEL_FEATURES)}


def what_if(**values):
    x = np.array([values[f] for f in MODEL_FEATURES])
    p = forest.predict([x])[0]
    effect = {}
    for i, f in enumerate(MODEL_FEATURES):
        x2 = x.copy(); x2[i] = med[i]
        effect[f] = p - forest.predict([x2])[0]
    s = pd.Series(effect).sort_values()
    colors = ["#1F5F8B" if v < 0 else "#A65400" for v in s]
    s.plot.barh(figsize=(6, 3.2), color=colors)
    plt.title(f"⟪predicted PM2.5:‖tahmin edilen PM2,5:⟫ {p:.1f} µg/m³"); plt.show()


out = widgets.interactive_output(what_if, sliders)
display(widgets.VBox(list(sliders.values())), out)""", "s4-wi")
    md("""### 4.5 ⟪Partial dependence‖Kısmi bağımlılık⟫

$$\\hat{f}_S(x_S) = \\frac{1}{n}\\sum_{i=1}^{n} \\hat{f}\\bigl(x_S, \\mathbf{x}_C^{(i)}\\bigr)$$""", "s4-pdp-md")
    code("""from sklearn.inspection import PartialDependenceDisplay

fig, ax = plt.subplots(figsize=(12, 3.2))
PartialDependenceDisplay.from_estimator(
    forest, Xm, features=[0, 7, 1, 2], feature_names=MODEL_FEATURES, ax=ax,
    kind="both", subsample=60, random_state=RANDOM_STATE)
plt.tight_layout(); plt.show()""", "s4-pdp")
    md("""### 4.6 ⟪The model surface in 3D‖Model yüzeyi 3B⟫""", "s4-surf-md")
    code("""ix = MODEL_FEATURES.index("vehicles_per_min")
iy = MODEL_FEATURES.index("background_pm25")
gx = np.linspace(Xm[:, ix].min(), Xm[:, ix].max(), 30)
gy = np.linspace(Xm[:, iy].min(), Xm[:, iy].max(), 30)
grid = np.tile(med, (900, 1))
grid[:, ix] = np.repeat(gx, 30)
grid[:, iy] = np.tile(gy, 30)
Zs = forest.predict(grid).reshape(30, 30).T
if HAS_PLOTLY:
    fig = go.Figure(go.Surface(x=gx, y=gy, z=Zs, colorscale="Blues"))
    fig.update_layout(scene=dict(xaxis_title="vehicles_per_min",
                                 yaxis_title="background_pm25", zaxis_title="PM2.5"),
                      height=520,
                      title="⟪Predicted PM2.5, other inputs at medians‖Tahmin edilen PM2,5, diğer girdiler medyanda⟫")
    fig.show()
else:
    ax = plt.figure(figsize=(7, 5)).add_subplot(projection="3d")
    GX, GY = np.meshgrid(gx, gy)
    ax.plot_surface(GX, GY, Zs, cmap="Blues"); plt.show()""", "s4-surf")
    md("""⟪**Observe and reflect.** The forest found the rules that generated the synthetic data. Which field observation would you need to believe the same importance on a real campus?‖**Gözlemle ve düşün.** Orman, sentetik veriyi üreten kuralları buldu. Aynı öneme gerçek bir kampüste inanmak için hangi saha gözlemine ihtiyaç duyardınız?⟫""", "s4-obs")

    # ------------------------------------------------------------------ 5
    md("""## 5. ⟪Share and turn into action‖Paylaş ve aksiyona dönüştür⟫

*⟪Workshop site: [Part 5](""" + SITE + """part5.html)‖Atölye sitesi: [5. Bölüm](""" + SITE + """tr/part5.html)⟫*

### 5.1 ⟪The fact table‖Olgu tablosu⟫""", "sec-5")
    code("""CAMPUS = "B"
facts = pd.concat([fair_table(visits, ch).assign(channel=ch)
                   for ch in ["pm25_ugm3", "temperature_c", "co2_ppm"]])
facts = facts[facts.campus == CAMPUS][["channel", "point_type", "round1", "round2",
                                       "two_round_mean", "minus_reference"]].round(1)
facts.to_csv(f"nokta_facts_{CAMPUS}.csv", index=False)
display(facts)""", "s5-facts")
    md("""### 5.2 ⟪A safe prompt‖Güvenli bir istem⟫""", "s5-prompt-md")
    code("""RULES = [
    "⟪Use only the numbers in the table, and write 'not measured' for a missing value.‖Yalnızca tablodaki sayıları kullan, eksik bir değer için 'ölçülmedi' yaz.⟫",
    "⟪Do not rank campuses, universities or cities.‖Kampüsleri, üniversiteleri ya da şehirleri sıralama.⟫",
    "⟪State that each value is the median of a 15-minute visit.‖Her değerin 15 dakikalık bir ziyaretin medyanı olduğunu belirt.⟫",
    "⟪Do not compare the values with 24-hour or annual guidelines.‖Değerleri 24 saatlik ya da yıllık kılavuzlarla karşılaştırma.⟫",
    "⟪Keep observation, interpretation and advice in separate paragraphs.‖Gözlemi, yorumu ve öneriyi ayrı paragraflarda tut.⟫",
    "⟪Mention low-cost sensors, humidity correction and offsets.‖Düşük maliyetli sensörleri, nem düzeltmesini ve sapmaları belirt.⟫",
    "⟪Use cautious verbs for causes.‖Nedenler için temkinli ifadeler kullan.⟫"]


def table_text(frame):
    try:
        return frame.to_markdown(index=False)          # ⟪needs the tabulate package‖tabulate paketi gerekir⟫
    except ImportError:
        return frame.to_string(index=False)


def make_prompt(facts, campus, audience="⟪a campus environment report‖bir kampüs çevre raporu⟫"):
    lines = ["⟪Role: You help a student team report campus measurements.‖Rol: Kampüs ölçümlerini raporlayan bir öğrenci ekibine yardım et.⟫",
             f"⟪Task: Write {audience} about Campus {campus}.‖Görev: Kampüs {campus} verisiyle {audience} yaz.⟫",
             "⟪Data:‖Veri:⟫", table_text(facts), "⟪Rules:‖Kurallar:⟫"]
    return "\\n".join(lines + ["- " + r for r in RULES])


print(make_prompt(facts, CAMPUS))""", "s5-prompt")
    md("""### 5.3 ⟪The number auditor‖Sayı denetleyicisi⟫

⟪Paste an AI-written text into `text`. The auditor lists every number and marks those that the fact table does not contain. A flagged number is not always wrong, for example a guideline value or a year, but every flagged number needs a source.‖YZ ile yazılmış bir metni `text` değişkenine yapıştırın. Denetleyici her sayıyı listeler ve olgu tablosunda bulunmayanları işaretler. İşaretli bir sayı her zaman yanlış değildir, örneğin bir kılavuz değeri ya da bir yıl olabilir. Ancak işaretli her sayı bir kaynak gerektirir.⟫""", "s5-audit-md")
    code(src(core.audit_numbers) + """


NUMBER = re.compile(r"(?<![\\w.,])-?\\d+(?:[.,]\\d+)?")
text = (""" + "⟪" + wrap_text(AUDIT_TEXT["en"]) + "‖" + wrap_text(AUDIT_TEXT["tr"]) + "⟫" + """)
audit = audit_numbers(text, facts)
display(audit)
print("⟪numbers without support in the table:‖tabloda desteği olmayan sayılar:⟫",
      int((~audit.supported).sum()))""", "s5-audit")
    md("""### ⟪Exercise 5.A‖Alıştırma 5.A⟫

⟪How many numbers of `text` does the auditor flag as unsupported?‖Denetleyici `text` içindeki kaç sayıyı desteksiz olarak işaretliyor?⟫""", "ex-5a-md")
    code("""answer = None   # your answer
check("Exercise 5.A", answer)""", "ex-5a")
    code("""#@title ⟪Reference solution (run this cell; open it only after trying)‖Örnek çözüm (bu hücreyi çalıştırın; ancak denedikten sonra açın)⟫
answer = int((~audit.supported).sum())
print(answer)
check("Exercise 5.A", answer)""", "ex-5a-sol")
    md("""### 5.4 ⟪The solution card‖Çözüm kartı⟫""", "s5-card-md")
    code("""def solution_card(table, problem, evidence, solution, feasibility, youth):
    parts = [("⟪Problem‖Sorun⟫", problem), ("⟪Evidence‖Dayanak⟫", evidence), ("⟪Solution‖Çözüm⟫", solution),
             ("⟪Feasibility‖Uygulanabilirlik⟫", feasibility), ("⟪Role of young people‖Gençlerin rolü⟫", youth)]
    return f"### {table}\\n\\n" + "\\n\\n".join(f"**{k}.** {v}" for k, v in parts)


row = facts[(facts.channel == "temperature_c") & (facts.point_type == "sunny_hard")]
card = solution_card(
    "⟪Microclimate and green campus‖Mikroiklim ve yeşil kampüs⟫",
    "⟪The concrete square heats up in the sun.‖Beton meydan güneşte ısınıyor.⟫",
    f"⟪Two-round mean‖İki tur ortalaması⟫ {row.minus_reference.iloc[0]:+.1f} °C"
    " ⟪against the reference point.‖referans noktasına göre.⟫",
    "⟪Shade sails over the benches and a row of trees.‖Bankların üzerine gölgelik ve bir sıra ağaç.⟫",
    "⟪Low cost for the sails, while trees need one season.‖Gölgelikler düşük maliyetlidir, ağaçlar ise bir mevsim gerektirir.⟫",
    "⟪Students measure again after one year with the same protocol.‖Öğrenciler bir yıl sonra aynı protokolle yeniden ölçer.⟫")
display(Markdown(card))""", "s5-card")

    md("""## ⟪Application challenges‖Uygulama görevleri⟫

| ⟪Field‖Alan⟫ | ⟪Challenge‖Görev⟫ |
|---|---|
| ⟪Engineering‖Mühendislik⟫ | ⟪Design a test that separates real heat at the sunny square from sunshine on the sensor housing.‖Güneşli meydandaki gerçek sıcaklığı sensör gövdesine vuran güneşten ayıran bir test tasarlayın.⟫ |
| ⟪Health sciences‖Sağlık bilimleri⟫ | ⟪Estimate how long a student waits at the bus stop each day and what the PM2.5 difference means for that time.‖Bir öğrencinin her gün otobüs durağında ne kadar beklediğini ve PM2,5 farkının bu süre için ne anlama geldiğini kestirin.⟫ |
| ⟪Social sciences‖Sosyal bilimler⟫ | ⟪Ask ten students where on campus they feel the air is worst and compare their answers with the fair table.‖On öğrenciye kampüste havayı en kötü nerede hissettiklerini sorun ve cevaplarını adil tabloyla karşılaştırın.⟫ |
| ⟪Communication‖İletişim⟫ | ⟪Turn one result into a figure for the congress that shows its averaging time and its uncertainty.‖Bir sonucu ortalama alma süresini ve belirsizliğini gösteren bir kongre şekline dönüştürün.⟫ |
| ⟪Economics and management‖İktisat ve işletme⟫ | ⟪Compare the cost per degree of shade sails and trees for the sunny square over ten years.‖Güneşli meydan için gölgelik ve ağaçların on yıllık derece başına maliyetini karşılaştırın.⟫ |
| ⟪Education‖Eğitim⟫ | ⟪Plan a 40-minute lesson in which pupils repeat the two-round design with a thermometer.‖Öğrencilerin iki turlu tasarımı bir termometreyle tekrarladığı 40 dakikalık bir ders planlayın.⟫ |""", "challenges")
    md("""## ⟪After the notebook‖Defterden sonra⟫

⟪Open the [debrief of the NOKTA Lab](""" + SITE + """lab.html#debrief) for a field report of the session. For the analysis days of 21 to 24 November, set `DATA_SOURCE = "own"` in Section 0 and run the notebook on your own NOKTA files.‖Oturumun saha raporu için [NOKTA Laboratuvarının değerlendirmesini](""" + SITE + """tr/lab.html#debrief) açın. 21-24 Kasım analiz günleri için 0. Bölümde `DATA_SOURCE = "own"` ayarını yapın ve defteri kendi NOKTA dosyalarınızla çalıştırın.⟫

**⟪References‖Kaynaklar⟫**

1. Leys, C., Ley, C., Klein, O., Bernard, P., & Licata, L. (2013). Detecting outliers: Do not use standard deviation around the mean, use absolute deviation around the median. *Journal of Experimental Social Psychology, 49*(4), 764–766. https://doi.org/10.1016/j.jesp.2013.03.013
2. Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008). Isolation forest. In *Proceedings of the 8th IEEE International Conference on Data Mining (ICDM 2008)* (pp. 413–422). https://doi.org/10.1109/ICDM.2008.17
3. Crilley, L. R., Shaw, M., Pound, R., Kramer, L. J., Price, R., Young, S., Lewis, A. C., & Pope, F. D. (2018). Evaluation of a low-cost optical particle counter (Alphasense OPC-N2) for ambient air monitoring. *Atmospheric Measurement Techniques, 11*(2), 709–720. https://doi.org/10.5194/amt-11-709-2018
4. Alduchov, O. A., & Eskridge, R. E. (1996). Improved Magnus form approximation of saturation vapor pressure. *Journal of Applied Meteorology, 35*(4), 601–609. https://doi.org/10.1175/1520-0450(1996)035<0601:IMFAOS>2.0.CO;2
5. Lloyd, S. P. (1982). Least squares quantization in PCM. *IEEE Transactions on Information Theory, 28*(2), 129–137. https://doi.org/10.1109/TIT.1982.1056489
6. Jolliffe, I. T., & Cadima, J. (2016). Principal component analysis: A review and recent developments. *Philosophical Transactions of the Royal Society A, 374*(2065), 20150202. https://doi.org/10.1098/rsta.2015.0202
7. Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5–32. https://doi.org/10.1023/A:1010933404324
8. Roberts, D. R., Bahn, V., Ciuti, S., Boyce, M. S., Elith, J., Guillera-Arroita, G., Hauenstein, S., Lahoz-Monfort, J. J., Schröder, B., Thuiller, W., Warton, D. I., Wintle, B. A., Hartig, F., & Dormann, C. F. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*(8), 913–929. https://doi.org/10.1111/ecog.02881
9. Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. *The Annals of Statistics, 29*(5), 1189–1232. https://doi.org/10.1214/aos/1013203451""", "after")
    md(SIGNATURE, "signature")
    return C


AUDIT_TEXT = {
    "en": ("On Campus B the road had the highest PM2.5, with a two-round mean of 21.7 "
           "µg/m³, 7.8 µg/m³ above the reference. The green area was the cleanest point "
           "at 6.1 µg/m³. Near the road PM2.5 exceeded the WHO 24-hour guideline of 15 "
           "µg/m³. A 2024 report confirms this. The sunny square was 3.6 °C warmer."),
    "tr": ("Kampüs B'de en yüksek PM2,5, iki tur ortalaması 21,7 µg/m³ ile yoldaydı ve "
           "referansın 7,8 µg/m³ üstündeydi. Yeşil alan 6,1 µg/m³ ile en temiz noktaydı. "
           "Yolun yakınında PM2,5, DSÖ'nün 15 µg/m³ olan 24 saatlik kılavuz değerini aştı. "
           "2024 tarihli bir rapor bunu doğruluyor. Güneşli meydan 3,6 °C daha sıcaktı."),
}


def expected_answers():
    """Compute the answers of the exercises with the same code as the notebook."""
    import numpy as np
    import pandas as pd
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    df = core.load_readings(ROOT / "data" / "nokta_synthetic.csv")
    forms = pd.read_csv(ROOT / "data" / "nokta_field_forms_synthetic.csv")
    coloc = pd.read_csv(ROOT / "data" / "nokta_colocation_synthetic.csv")
    flags = core.flag_quality(df)
    adj = core.correct_pm(core.apply_offsets(core.clean_readings(df, flags),
                                             core.colocation_offsets(coloc)))
    minutes = core.minute_table(adj)
    visits = core.visit_table(minutes)
    ft = core.fair_table(visits, "temperature_c")
    green = ft[(ft.campus == "A") & (ft.point_type == "green")]["minus_reference"].iloc[0]
    anom = core.add_anomalies(minutes)
    Z, _, _ = core.standardize(anom[core.CLUSTER_FEATURES].to_numpy())
    sil = {k: silhouette_score(Z, KMeans(n_clusters=k, n_init=10, random_state=core.RANDOM_STATE)
                               .fit(Z).labels_) for k in range(2, 7)}
    facts = pd.concat([core.fair_table(visits, ch).assign(channel=ch)
                       for ch in ["pm25_ugm3", "temperature_c", "co2_ppm"]])
    facts = facts[facts.campus == "B"][["channel", "point_type", "round1", "round2",
                                         "two_round_mean", "minus_reference"]].round(1)
    out = {}
    for lang in ("en", "tr"):
        audit = core.audit_numbers(AUDIT_TEXT[lang], facts)
        out[lang] = int((~audit.supported).sum())
    assert out["en"] == out["tr"], out
    return {
        "Exercise 1.A": round(float(core.robust_z(np.array([14.2, 15.0, 13.8, 14.6, 97.3,
                                                           15.1, 14.4]))[4]), 4),
        "Exercise 2.A": round(float(green), 4),
        "Exercise 2.B": round(float(core.dew_point(20.0, 50.0)), 4),
        "Exercise 3.A": int(max(sil, key=sil.get)),
        "Exercise 4.A": "vehicles_per_min",
        "Exercise 5.A": out["en"],
    }


def build():
    expected = expected_answers()
    spec = cells(expected)
    (ROOT / "notebooks").mkdir(exist_ok=True)
    for lang in ("en", "tr"):
        nb = new_notebook()
        nb.metadata = {"colab": {"provenance": [], "toc_visible": True},
                       "kernelspec": {"name": "python3", "display_name": "Python 3"},
                       "language_info": {"name": "python"}}
        for kind, text, cid in spec:
            body = pick(text, lang)
            cell = new_markdown_cell(body) if kind == "md" else new_code_cell(body)
            cell["id"] = cid
            cell.metadata["id"] = cid
            if kind == "code" and body.startswith("#@title"):
                cell.metadata["cellView"] = "form"
            nb.cells.append(cell)
        nbformat.validate(nb)
        nbformat.write(nb, ROOT / "notebooks" / NB_NAME[lang])
    print("notebooks written; expected answers:", expected)


if __name__ == "__main__":
    build()
