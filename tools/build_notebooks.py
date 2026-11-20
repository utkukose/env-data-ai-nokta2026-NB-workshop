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

⟪Save a copy to your Drive first (File, Save a copy in Drive), so that your changes are kept. Then run the cells in order with Shift+Enter, because later cells use the results of earlier ones. Each section belongs to the part of the [workshop site](""" + SITE + """) with the same number, from Section 1 for Part 1 to Section 5 for Part 5. Section 0 loads the data, and no installation is needed on Colab.‖Önce Drive'ınıza bir kopya kaydedin (Dosya, Drive'a kopya kaydet). Böylece yaptığınız değişiklikler korunur. Ardından hücreleri Shift+Enter ile sırayla çalıştırın, çünkü sonraki hücreler önceki hücrelerin sonuçlarını kullanmaktadır. Defterin her kısmı, [atölye sitesinde](""" + SITE + """tr/) aynı numarayı taşıyan bölüme karşılık gelir: Defterin 1. kısmı sitenin 1. Bölümüne, 5. kısmı da sitenin 5. Bölümüne aittir. 0. kısım veriyi yükler. Colab'da herhangi bir kurulum gerekmez.⟫

⟪Four kinds of cells guide the work. **Python note** cells explain a piece of the Python language where it first appears. **Exercises** ask for one number or name and check the answer at once with `check(...)`. Their reference solutions sit in folded cells, which should be opened only after a real attempt. **Observe and reflect** cells ask open questions about an output and have no solution cell, because the answer depends on your own reasoning. The data are synthetic and follow the NOKTA field protocol, and Section 0 shows how to load real NOKTA files instead.‖Dört tür hücre çalışmaya yol gösterir. **Python notu** hücreleri Python dilinin bir parçasını ilk kullanıldığı yerde açıklar. **Alıştırmalar** tek bir sayı ya da ad ister ve cevabı `check(...)` ile hemen denetler. Örnek çözümleri katlanmış hücrelerdedir ve ancak gerçekten denedikten sonra açılmalıdır. **Gözlemle ve düşün** hücreleri bir çıktı hakkında açık uçlu sorular sorar. Bu hücrelerin çözümü yoktur, çünkü cevap sizin kendi akıl yürütmenize bağlıdır. Veriler sentetiktir ve NOKTA saha protokolünü izler. 0. kısım bunun yerine gerçek NOKTA dosyalarının nasıl yükleneceğini gösterir.⟫""", "howto")

    # ------------------------------------------------------------------ 0
    md("""## 0. ⟪Setup and data‖Kurulum ve veri⟫

⟪The first cell loads the libraries and defines the order, colors and names of the six point types, together with the helper `check` that grades the exercises. The second cell keeps the expected answers of the exercises in a folded form. The third cell reads four files: The readings (one row every 10 seconds), the field forms (one row per visit), the side-by-side test of the three stations and, for the synthetic data only, a list of the problems that were planted on purpose. When a file is not found next to the notebook, it is downloaded from GitHub.‖İlk hücre kütüphaneleri yükler, altı nokta türünün sırasını, renklerini ve adlarını tanımlar. Alıştırmaları puanlayan `check` yardımcısı da bu hücrededir. İkinci hücre alıştırmaların beklenen cevaplarını katlanmış bir biçimde tutar. Üçüncü hücre dört dosya okur: Ölçümler (her 10 saniyede bir satır), saha formları (her ziyaret için bir satır), üç istasyonun yan yana testi ve yalnızca sentetik veride bulunan, bilerek yerleştirilmiş sorunların listesi. Bir dosya defterin yanında bulunamazsa GitHub'dan indirilir.⟫

⟪**Your own NOKTA data.** Set `DATA_SOURCE = "own"` and upload your CSV files with the columns of `data/nokta_template.csv` through the Files panel on the left. Their names are set in `OWN_FILES`. If your logger uses other column names, fill `COLUMN_MAP`, for example `{"Temp": "temperature_c"}`. Everything after this cell then runs on your data.‖**Kendi NOKTA veriniz.** `DATA_SOURCE = "own"` yapın ve `data/nokta_template.csv` sütunlarına sahip CSV dosyalarınızı soldaki Dosyalar paneliyle yükleyin. Dosya adları `OWN_FILES` sözlüğünde belirtilir. Kayıt cihazınız başka sütun adları kullanıyorsa `COLUMN_MAP` sözlüğünü doldurun, örneğin `{"Temp": "temperature_c"}`. Bu hücreden sonraki her şey sizin verinizle çalışır.⟫""", "sec-0")
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
    md("""⟪**Python note.** `f"..."` is a formatted text: Values inside `{ }` are written into it. `round(x, 2)` keeps two decimals, `sorted(...)` returns a sorted copy and `//` divides without the remainder, so `sorted(pm)[len(pm) // 2]` is the middle value of the sorted list. The output already previews Part 2: The single reading of 97.3 lifts the mean to 26.34, while the median stays at 14.6.‖**Python notu.** `f"..."` biçimlendirilmiş bir metindir: `{ }` içindeki değerler metne yazılır. `round(x, 2)` iki ondalık basamak bırakır, `sorted(...)` sıralanmış bir kopya döndürür, `//` ise kalansız böler. Bu yüzden `sorted(pm)[len(pm) // 2]` sıralanmış listenin ortadaki değeridir. Çıktı, atölye sitesinin 2. Bölümündeki konuyu şimdiden göstermektedir: Tek bir 97,3 ölçümü ortalamayı 26,34'e çıkarır, medyan ise 14,6'da kalır.⟫""", "py-note-1")

    # ------------------------------------------------------------------ 1
    md("""## 1. ⟪Measure: The campus as data‖Ölç: Veri olarak kampüs⟫

*⟪Workshop site: [Part 1](""" + SITE + """part1.html)‖Atölye sitesi: [1. Bölüm](""" + SITE + """tr/part1.html)⟫*

⟪Section 1 turns the raw readings into the table of clean minutes that Sections 2 to 4 use. It flags the typical faults of low-cost sensors, removes the offsets between the three stations, corrects the particle readings for humidity and finally summarizes every visit minute by minute.‖Defterin 1. kısmı ham ölçümleri, 2-4. kısımların kullandığı temiz dakika tablosuna dönüştürür. Düşük maliyetli sensörlerin tipik hatalarını işaretler, üç istasyon arasındaki sapmaları giderir, partikül ölçümlerini neme göre düzeltir ve son olarak her ziyareti dakika dakika özetler.⟫

### 1.1 ⟪Load and look‖Yükle ve bak⟫

⟪The function `load_readings` reads the readings file, turns the time stamps into dates and builds a label for every visit. The label `A-R1-P2`, for example, stands for Campus A, Round 1 and point P2. The cell then loads the field forms and the side-by-side test and prints how many readings, visits and campuses there are. The small table at the end counts the points measured in each campus and round, which should be six everywhere.‖`load_readings` fonksiyonu ölçüm dosyasını okur, zaman damgalarını tarihe çevirir ve her ziyaret için bir etiket oluşturur. Örneğin `A-R1-P2` etiketi Kampüs A, 1. tur ve P2 noktasını gösterir. Hücre ardından saha formlarını ve yan yana testi yükler, ölçüm, ziyaret ve kampüs sayılarını yazdırır. Sondaki küçük tablo her kampüs ve turda ölçülen nokta sayısını verir. Bu sayı her yerde altı olmalıdır.⟫""", "sec-1")
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
    md("""⟪The next cell plots one visit: The point near traffic on Campus A in Round 1. Its three panels show temperature, PM2.5 and CO₂ against the minutes since the station arrived. The orange band marks the first two minutes, when the sensors are still adjusting to the new place. The short peaks of PM2.5 and CO₂ are plumes from passing vehicles.‖Sonraki hücre tek bir ziyareti çizer: Kampüs A'da 1. turdaki trafiğe yakın nokta. Üç panel sıcaklığı, PM2,5 değerini ve CO₂'yi istasyonun varışından sonraki dakikalara göre gösterir. Turuncu bant, sensörlerin yeni yere henüz uyum sağladığı ilk iki dakikayı işaretler. PM2,5 ve CO₂'deki kısa tepeler, geçen araçların bıraktığı bulutlardır.⟫""", "s1-plot-md")
    code("""visit = df[df["visit"] == "A-R1-P2"]     # ⟪Campus A, Round 1, near traffic‖Kampüs A, 1. tur, trafiğe yakın⟫
fig, axes = plt.subplots(1, 3, figsize=(13, 3.2))
for ax, ch in zip(axes, ["temperature_c", "pm25_ugm3", "co2_ppm"]):
    ax.plot(visit["seconds_since_arrival"] / 60, visit[ch], lw=1.4, color="#0E7A5F")
    ax.axvspan(0, 2, color="#eda100", alpha=0.15)
    ax.set_title(ch); ax.set_xlabel("⟪minutes since arrival‖varıştan sonraki dakika⟫")
plt.tight_layout(); plt.show()""", "s1-plot")

    md("""### 1.2 ⟪Quality flags‖Kalite işaretleri⟫

⟪Raw data are never changed. The function `flag_quality` adds one true-or-false column per problem instead: The warm-up in the first 120 seconds after a move, logger gaps, a light sensor at its 16-bit limit of 65,535 lx, relative humidity above 85 %, single-channel particle glitches, CO₂ values outside 300 to 2,000 ppm and a frozen CO₂ sensor whose value does not change for 12 readings in a row. The glitch test uses the modified z-score of Part 1 [1]:‖Ham veri asla değiştirilmez. `flag_quality` fonksiyonu bunun yerine her sorun için doğru ya da yanlış değerli bir sütun ekler: Taşımadan sonraki ilk 120 saniyedeki ısınma, kayıt boşlukları, 65.535 lx olan 16 bitlik sınırına ulaşmış ışık sensörü, %85'in üzerindeki bağıl nem, tek kanalda görülen partikül hataları, 300-2.000 ppm aralığının dışındaki CO₂ değerleri ve değeri art arda 12 ölçüm boyunca hiç değişmeyen donmuş bir CO₂ sensörü. Hata testi, atölye sitesinin 1. Bölümünde anlatılan değiştirilmiş z-skorunu kullanır [1]:⟫

$$M_i = \\frac{⟪0.6745‖0{,}6745⟫\\,(x_i - \\tilde{x})}{\\mathrm{MAD}}, \\qquad \\mathrm{MAD} = \\operatorname{median}_i \\lvert x_i - \\tilde{x} \\rvert$$

⟪Here x<sub>i</sub> is one reading, x̃ is the median of the readings and MAD is the median of the absolute deviations from it. The factor 0.6745 makes M comparable with an ordinary z-score when the data are normally distributed. The median and the MAD hardly react to a few extreme values, so a single spike cannot hide itself by inflating the spread.‖Burada x<sub>i</sub> tek bir ölçüm, x̃ ölçümlerin medyanı, MAD ise medyandan mutlak sapmaların medyanıdır. 0,6745 çarpanı, veri normal dağıldığında M değerini olağan bir z-skoruyla karşılaştırılabilir kılar. Medyan ve MAD birkaç uç değerden neredeyse etkilenmez. Bu yüzden tek bir sıçrama, yayılımı büyüterek kendini gizleyemez.⟫

*⟪From the formulas to the code: `robust_z` computes M. `spike_scores` applies it to the distance of each reading from a running median of five readings, so the slow changes during a visit do not count as spikes. A particle reading is flagged when three conditions hold together: |M| > 6, the reading is more than twice the running median, and only one of the three particle sizes jumps. The last condition reflects that a real plume lifts all sizes together.‖Formüllerden koda: `robust_z` M değerini hesaplar. `spike_scores` bunu her ölçümün beş ölçümlük kayan medyandan uzaklığına uygular. Böylece bir ziyaret boyunca görülen yavaş değişimler sıçrama sayılmaz. Bir partikül ölçümü üç koşul birlikte sağlandığında işaretlenir: |M| > 6 olmalı, ölçüm kayan medyanın iki katından büyük olmalı ve üç partikül boyutundan yalnızca biri sıçramalıdır. Son koşulun nedeni, gerçek bir bulutun bütün boyutları birlikte yükseltmesidir.⟫*""", "s1-qc-md")
    code(src(core.robust_z, core.spike_scores, core.flag_quality, core.clean_readings) + """


flags = flag_quality(df)
display(flags.sum().rename("⟪flagged readings‖işaretli ölçüm⟫").to_frame().T)""", "s1-qc")
    md("""⟪The next cell scores the flags against the problems planted in the synthetic data. For each problem, `planted` counts the readings that carry it, `flagged` counts the readings that the rule marked and `caught` counts the planted readings among them. Two PM2.5 glitches are missed, because they fall inside real plumes, where a single-channel spike is hard to tell apart from real pollution. The plot then shows CO₂ during the first visit of Campus B in Round 1. The readings of a frozen sensor and one value out of range are circled, and the orange band marks the warm-up.‖Sonraki hücre işaretleri sentetik veriye yerleştirilmiş sorunlarla karşılaştırarak puanlar. Her sorun için `planted` o sorunu taşıyan ölçümleri, `flagged` kuralın işaretlediği ölçümleri, `caught` ise bunlar arasındaki yerleştirilmiş ölçümleri sayar. İki PM2,5 hatası kaçırılır, çünkü gerçek bulutların içine düşerler ve orada tek kanaldaki bir sıçramayı gerçek kirlilikten ayırmak zordur. Grafik ardından Kampüs B'nin 1. turundaki ilk ziyarette CO₂ değerlerini gösterir. Donmuş sensörün ölçümleri ve aralık dışındaki bir değer halkayla, ısınma süresi de turuncu bantla işaretlenmiştir.⟫""", "s1-score-md")
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

⟪Rules catch the problems that someone thought of in advance. An Isolation Forest looks instead for readings that are easy to separate from the rest in all channels at once [2]. It builds random trees that split the data at random values, and a reading that ends up alone after only a few splits is unusual. Before training, every channel is expressed as its difference from the median of its own visit, so the forest compares readings within a visit rather than campuses or hours. The setting `contamination=0.02` asks it to flag the 2 % of readings that are easiest to isolate. The cell prints how many readings the forest flags, how many of them a rule has also flagged and a few readings that only the forest found. Its flags are a list to review with the field notes, not a list to delete.‖Kurallar, birinin önceden düşündüğü sorunları yakalar. Isolation Forest ise bütün kanallarda aynı anda geri kalanlardan kolayca ayrılan ölçümleri arar [2]. Veriyi rastgele değerlerden bölen rastgele ağaçlar kurar. Yalnızca birkaç bölmeden sonra tek başına kalan bir ölçüm olağan dışıdır. Eğitimden önce her kanal kendi ziyaretinin medyanından farkı olarak ifade edilir. Böylece orman kampüsleri ya da saatleri değil, aynı ziyaretteki ölçümleri karşılaştırır. `contamination=0.02` ayarı, ormandan ayrılması en kolay %2'lik ölçümü işaretlemesini ister. Hücre ormanın kaç ölçümü işaretlediğini, bunlardan kaçını bir kuralın da işaretlediğini ve yalnızca ormanın bulduğu birkaç ölçümü yazdırır. Ormanın işaretleri silinecek değil, saha notlarıyla gözden geçirilecek bir listedir.⟫""", "s1-if-md")
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
    md("""⟪**Missing is not zero.** In Round 2 on Campus A, the logger restarted at P5 and left six empty readings. The next cell takes the 22 readings around the gap and computes the mean temperature twice: Once with the empty readings skipped and once with them written as zero. The difference shows why a gap must stay empty in the data.‖**Eksik değer sıfır değildir.** Kampüs A'nın 2. turunda kayıt cihazı P5 noktasında yeniden başladı ve altı boş ölçüm bıraktı. Sonraki hücre boşluğun çevresindeki 22 ölçümü alır ve ortalama sıcaklığı iki kez hesaplar: Bir kez boş ölçümler atlanarak, bir kez de sıfır yazılarak. Aradaki fark, bir boşluğun veride neden boş kalması gerektiğini göstermektedir.⟫""", "s1-gap-md")
    code("""gap = df[df["visit"] == "A-R2-P5"]["temperature_c"].iloc[30:52]
print("⟪skipped:‖atlanınca:⟫", round(gap.mean(), 2), "°C   ⟪written as zero:‖sıfır yazılınca:⟫",
      round(gap.fillna(0).mean(), 2), "°C")""", "s1-gap")

    md("""### 1.4 ⟪Three stations, one story‖Üç istasyon, tek hikâye⟫

⟪Before the field rounds, the three stations ran side by side for two hours. Since they measured the same air, a lasting difference between them is an offset of the device. The offset of station s is its mean difference from the mean of the three stations:‖Saha turlarından önce üç istasyon iki saat boyunca yan yana çalıştırıldı. Aynı havayı ölçtükleri için aralarında kalıcı bir fark varsa bu, cihazın kendi sapmasıdır. s istasyonunun sapması, üç istasyonun ortalamasından ortalama farkıdır:⟫

$$o_s = \\frac{1}{T}\\sum_{t=1}^{T}\\bigl(x_s(t) - \\bar{x}(t)\\bigr)$$

⟪Here x<sub>s</sub>(t) is the reading of station s in minute t of the test, x̄(t) is the mean of the three stations in that minute and T is the number of minutes. For temperature, humidity and CO₂ the offset is subtracted from every field reading of the station. For particles a ratio is used instead, because the readings of optical sensors tend to differ in proportion to the concentration. The readings are then divided by the mean ratio of the station to the three-station mean.‖Burada x<sub>s</sub>(t), s istasyonunun testin t. dakikasındaki ölçümü, x̄(t) aynı dakikada üç istasyonun ortalaması, T ise dakika sayısıdır. Sıcaklık, nem ve CO₂ için bu sapma istasyonun her saha ölçümünden çıkarılır. Partiküller için ise bir oran kullanılır, çünkü optik sensörlerin ölçümleri genellikle derişimle orantılı olarak farklılaşır. Bu durumda ölçümler, istasyonun üç istasyon ortalamasına göre ortalama oranına bölünür.⟫

*⟪From the formulas to the code: `colocation_offsets` computes o for temperature, humidity and CO₂ and the ratio `pm_ratio` for particles. `apply_offsets` then subtracts the offsets and divides by the ratio.‖Formüllerden koda: `colocation_offsets` sıcaklık, nem ve CO₂ için o değerini, partiküller için ise `pm_ratio` oranını hesaplar. `apply_offsets` ardından sapmaları çıkarır ve ölçümleri bu orana böler.⟫*""", "s1-coloc-md")
    code(src(core.colocation_offsets, core.apply_offsets) + """


offsets = colocation_offsets(coloc)
display(offsets.round(3))""", "s1-coloc")

    md("""### 1.5 ⟪Humid air and the particle counter‖Nemli hava ve partikül sayacı⟫

⟪In humid air, particles take up water and grow. An optical sensor sees the larger wet particles and reports more mass than the dry particles have. The κ-Köhler correction used by Crilley et al. [3] divides the reading by a growth factor C:‖Nemli havada partiküller su alır ve büyür. Optik sensör bu büyümüş ıslak partikülleri görür ve kuru partiküllerin gerçek kütlesinden daha fazla kütle bildirir. Crilley vd. [3] tarafından kullanılan κ-Köhler düzeltmesi, ölçümü bir C büyüme çarpanına böler:⟫

$$C(a_w) = 1 + \\frac{\\kappa\\,\\rho_w/\\rho_p}{-1 + 1/a_w}, \\qquad a_w = \\mathrm{RH}/100$$

⟪Here a<sub>w</sub> is the water activity, equal to the relative humidity RH divided by 100. κ is the hygroscopicity of the particles, ρ<sub>w</sub> = 1 g/cm³ is the density of water and ρ<sub>p</sub> is the density of the dry particles. The workshop uses κ = 0.3 and ρ<sub>p</sub> = 1.65 g/cm³. At 85 % relative humidity, for example, C = 1 + (0.3 / 1.65) / (1/0.85 − 1) = 1 + 0.182 / 0.176 ≈ 2.03. The corrected reading is then about half of the raw one. The cell prints C for four humidity levels. A real study would estimate κ for the local air against a reference instrument.‖Burada a<sub>w</sub> suyun aktivitesidir ve bağıl nemin (RH) 100'e bölümüne eşittir. κ partiküllerin higroskopikliğini, ρ<sub>w</sub> = 1 g/cm³ suyun yoğunluğunu, ρ<sub>p</sub> ise kuru partiküllerin yoğunluğunu gösterir. Atölyede κ = 0,3 ve ρ<sub>p</sub> = 1,65 g/cm³ kullanılmaktadır. Örneğin %85 bağıl nemde C = 1 + (0,3 / 1,65) / (1/0,85 − 1) = 1 + 0,182 / 0,176 ≈ 2,03 olur. Yani düzeltilmiş ölçüm ham ölçümün yaklaşık yarısıdır. Hücre dört nem düzeyi için C değerini yazdırır. Gerçek bir çalışma ise κ değerini yerel hava için bir referans cihazla kestirmelidir.⟫""", "s1-hum-md")
    code(src(core.humidity_factor, core.correct_pm) + """


for rh in (50, 70, 85, 90):
    print(f"RH {rh} %  ->  C = {humidity_factor(rh):.2f}")""", "s1-hum")

    md("""### 1.6 ⟪The table of clean minutes‖Temiz dakika tablosu⟫

⟪This cell puts the steps of Section 1 together. Flagged values become missing, never zero. The station offsets are then removed, the particles are corrected for humidity and every visit is summarized minute by minute with the median of each channel. The first two minutes of every visit drop out, because the warm-up flag empties all their channels. The table is saved as `nokta_clean_minutes.csv`, and Sections 2 to 4 start from it. The small table at the end compares raw and corrected PM2.5 on Campus C in Round 2, the most humid morning of the data. It also gives the relative humidity at each point.‖Bu hücre 1. kısmın adımlarını bir araya getirir. İşaretli değerler eksik yapılır, asla sıfır yapılmaz. Ardından istasyon sapmaları giderilir, partiküller neme göre düzeltilir ve her ziyaret, her kanalın medyanıyla dakika dakika özetlenir. Her ziyaretin ilk iki dakikası tablodan çıkar, çünkü ısınma işareti bu dakikaların bütün kanallarını boşaltır. Tablo `nokta_clean_minutes.csv` adıyla kaydedilir ve 2-4. kısımlar bu tablodan başlar. Sondaki küçük tablo, verideki en nemli sabah olan Kampüs C'nin 2. turunda ham ve düzeltilmiş PM2,5 değerlerini her noktanın bağıl nemiyle birlikte karşılaştırır.⟫""", "s1-min-md")
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

⟪Section 2 compares the points fairly. It removes the effect of the clock with the two-round design and describes typical values with robust statistics. It then checks a correlation inside groups and separates moisture from temperature with the dew point.‖Defterin 2. kısmı noktaları adil biçimde karşılaştırır. İki turlu tasarımla saatin etkisini giderir, tipik değerleri dayanıklı istatistiklerle anlatır, bir korelasyonu grupların içinde sınar ve çiy noktasıyla nemi sıcaklıktan ayırır.⟫

### 2.1 ⟪The clock behind every point‖Her noktanın arkasındaki saat⟫

⟪The function `visit_table` summarizes every visit by the median of its clean minutes and keeps the clock time of the visit in the column `hour`. The plot shows the temperature of the six points of Campus A against the clock, with Round 1 as a solid line and Round 2 as a dashed line. Each dot takes the color of its point type. Both lines tend to rise through the morning, because the air warms, while each point adds its own effect. A point visited late in one round is visited early in the other, so a single round mixes the effect of the place with the effect of the hour.‖`visit_table` fonksiyonu her ziyareti temiz dakikalarının medyanıyla özetler ve ziyaretin saatini `hour` sütununda tutar. Grafik, Kampüs A'daki altı noktanın sıcaklığını saate göre gösterir. 1. tur düz, 2. tur kesikli çizgiyle çizilir ve her nokta kendi türünün rengini alır. Hava ısındığı için iki çizgi de sabah boyunca yükselme eğilimindedir, her nokta ise buna kendi etkisini ekler. Bir turda geç ziyaret edilen nokta diğer turda erken ziyaret edilir. Bu yüzden tek bir tur, yerin etkisini saatin etkisiyle karıştırır.⟫""", "sec-2")
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

$$\\bar{x}_p = \\frac{x_{p,1} + x_{p,2}}{2}, \\qquad \\Delta_p = \\bar{x}_p - \\bar{x}_{\\text{ref}}$$

⟪Here x<sub>p,1</sub> and x<sub>p,2</sub> are the visit medians of point p in Rounds 1 and 2, x̄<sub>p</sub> is their mean and Δ<sub>p</sub> is its difference from the two-round mean of the quiet reference point of the same campus. Suppose the morning warms by b °C per hour. The visit in slot k of Round 1 is paired with the visit in slot 5 − k of Round 2. Every point therefore receives the same total drift, and the drift cancels in Δ<sub>p</sub>. The function `fair_table` returns these columns for every campus and point type. The bar chart then shows Δ<sub>p</sub> for PM2.5 on all three campuses: A bar to the right of zero marks a point with more PM2.5 than the reference point.‖Burada x<sub>p,1</sub> ve x<sub>p,2</sub>, p noktasının 1. ve 2. turdaki ziyaret medyanları, x̄<sub>p</sub> bunların ortalaması, Δ<sub>p</sub> ise bu ortalamanın aynı kampüsteki sakin referans noktasının iki tur ortalamasından farkıdır. Sabahın saatte b °C ısındığını varsayalım. 1. turun k. sırasındaki ziyaret, 2. turun 5 − k. sırasındaki ziyaretle eşleşir. Böylece her nokta aynı toplam kaymayı alır ve kayma Δ<sub>p</sub> içinde birbirini götürür. `fair_table` fonksiyonu bu sütunları her kampüs ve nokta türü için verir. Çubuk grafik ardından üç kampüsün tamamında PM2,5 için Δ<sub>p</sub> değerini gösterir: Sıfırın sağındaki bir çubuk, referans noktasından daha fazla PM2,5 bulunan bir noktayı işaretler.⟫""", "s2-fair-md")
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
    md("""### 2.3 ⟪Typical values‖Tipik değerler⟫

⟪The function `add_anomalies` expresses every minute as its difference from the median of its own campus and round. A cool morning on the highland and a mild morning at the coast can then share one plot. The box plots show these PM2.5 differences for each point type. A box spans the middle half of the minutes, from the first to the third quartile, the line inside it is the median and the small triangle is the mean. Near the busy entrance and the road, short plumes stretch the upper whisker and pull the mean above the median. The table under the plot gives both values for every point type.‖`add_anomalies` fonksiyonu her dakikayı kendi kampüsünün ve turunun medyanından farkı olarak ifade eder. Böylece yüksek kampüsteki serin bir sabah ile kıyıdaki ılık bir sabah aynı grafikte yer alabilir. Kutu grafikleri her nokta türü için bu PM2,5 farklarını gösterir. Kutu, birinci çeyrekten üçüncü çeyreğe kadar dakikaların ortadaki yarısını kapsar. Kutunun içindeki çizgi medyanı, küçük üçgen ise ortalamayı gösterir. Kalabalık girişin ve yolun yakınında kısa süreli bulutlar üst bıyığı uzatır ve ortalamayı medyanın üstüne çeker. Grafiğin altındaki tablo her nokta türü için iki değeri de verir.⟫""", "s2-box-md")
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
    md("""### 2.4 ⟪Related or caused?‖İlişki mi, neden mi?⟫

$$r = \\frac{\\sum_i (x_i - \\bar{x})(y_i - \\bar{y})}{\\sqrt{\\sum_i (x_i - \\bar{x})^2}\\,\\sqrt{\\sum_i (y_i - \\bar{y})^2}}$$

⟪Here x<sub>i</sub> is the temperature and y<sub>i</sub> the air pressure of minute i, while x̄ and ȳ are their means. The Pearson correlation r lies between −1 and +1 and measures how well a straight line fits the cloud of points. The cell computes r first over all clean minutes and then inside each campus and round. Over all minutes r is clearly positive, but inside every group it is negative. The coastal campus is both warmer and lower, so its minutes combine high temperature with high pressure, and this alone creates the positive value. Inside a group the pressure falls slowly during the morning while the air warms. This reversal is known as Simpson's paradox. The heat map at the end shows the correlations of all ten channels.‖Burada x<sub>i</sub>, i. dakikanın sıcaklığı, y<sub>i</sub> ise hava basıncıdır. x̄ ve ȳ bunların ortalamalarıdır. Pearson korelasyonu r, −1 ile +1 arasında değişir ve noktaların oluşturduğu buluta bir doğrunun ne kadar iyi uyduğunu ölçer. Hücre r değerini önce bütün temiz dakikalar için, ardından her kampüs ve turun kendi içinde hesaplar. Bütün dakikalarda r belirgin biçimde pozitiftir, ancak her grubun içinde negatiftir. Kıyı kampüsü hem daha sıcak hem de daha alçaktadır. Bu yüzden dakikaları yüksek sıcaklığı yüksek basınçla birleştirir ve pozitif değeri tek başına bu durum yaratır. Bir grubun içinde ise hava ısınırken basınç sabah boyunca yavaşça düşer. Bu tersine dönüş Simpson paradoksu olarak bilinmektedir. Sondaki ısı haritası on kanalın tamamı arasındaki korelasyonları gösterir.⟫""", "s2-corr-md")
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

⟪Relative humidity depends on temperature: The same air shows a higher relative humidity when it cools. The dew point removes this dependence. It is the temperature to which the air would have to cool for its water vapor to condense. It therefore changes only when the amount of water in the air changes. The Magnus form [4] gives it from temperature and relative humidity:‖Bağıl nem sıcaklığa bağlıdır: Aynı hava soğuduğunda daha yüksek bir bağıl nem gösterir. Çiy noktası bu bağımlılığı ortadan kaldırır. Çiy noktası, havadaki su buharının yoğuşması için havanın soğuması gereken sıcaklıktır. Bu yüzden yalnızca havadaki su miktarı değiştiğinde değişir. Magnus biçimi [4], çiy noktasını sıcaklıktan ve bağıl nemden hesaplar:⟫

$$\\gamma = \\ln\\frac{\\mathrm{RH}}{100} + \\frac{a\\,T}{b + T}, \\qquad T_d = \\frac{b\\,\\gamma}{a - \\gamma}, \\quad a = ⟪17.625‖17{,}625⟫,\\ b = ⟪243.04‖243{,}04⟫\\ ^\\circ\\mathrm{C}$$

⟪Here T is the air temperature in °C, RH the relative humidity in percent, γ an intermediate quantity and T<sub>d</sub> the dew point in °C. The constants a and b come from the fit of Alduchov and Eskridge [4]. The cell adds the dew point to every clean minute and prints its median for each campus, round and point type.‖Burada T °C cinsinden hava sıcaklığı, RH yüzde olarak bağıl nem, γ bir ara büyüklük, T<sub>d</sub> ise °C cinsinden çiy noktasıdır. a ve b sabitleri Alduchov ve Eskridge'in [4] uyarladığı değerlerdir. Hücre her temiz dakikaya çiy noktasını ekler ve her kampüs, tur ve nokta türü için medyanını yazdırır.⟫""", "s2-dew-md")
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

⟪Section 3 lets k-means group the clean minutes without being told where they were measured [5]. It then chooses the number of groups with two scores and compresses six channels with principal component analysis [7].‖Defterin 3. kısmı, k-ortalamalar algoritmasının temiz dakikaları nerede ölçüldüklerini bilmeden gruplamasını sağlar [5]. Ardından grup sayısını iki skorla seçer ve altı kanalı temel bileşenler analiziyle sıkıştırır [7].⟫

### 3.1 ⟪Standardize‖Standartlaştır⟫

⟪Each minute is described by three features: `temp_anomaly`, its temperature difference from the median of its campus and round, `log10_lux`, the logarithm of its light level, and `pm25_anomaly`, its PM2.5 difference. The logarithm is used for light, because the light level ranges from under ten thousand lux in shade to the sensor limit of 65,535 lux in full sun. Before k-means measures distances, every feature is standardized:‖Her dakika üç özellikle tanımlanır: Kampüsünün ve turunun medyanından sıcaklık farkı olan `temp_anomaly`, ışık şiddetinin logaritması olan `log10_lux` ve PM2,5 farkı olan `pm25_anomaly`. Işık için logaritma kullanılır, çünkü aydınlık düzeyi gölgede on bin lüksün altından tam güneşte sensörün 65.535 lükslük sınırına kadar uzanır. k-ortalamalar uzaklıkları ölçmeden önce her özellik standartlaştırılır:⟫

$$z_{ij} = \\frac{x_{ij} - \\mu_j}{\\sigma_j}$$

⟪Here x<sub>ij</sub> is the value of feature j in minute i, and μ<sub>j</sub> and σ<sub>j</sub> are the mean and the standard deviation of that feature. After this step every feature has a mean of 0 and a standard deviation of 1. One degree of temperature and one microgram of particles then no longer carry different weights in the distances. The cell prints μ and σ of the three features.‖Burada x<sub>ij</sub>, i. dakikada j. özelliğin değeri, μ<sub>j</sub> ve σ<sub>j</sub> ise o özelliğin ortalaması ve standart sapmasıdır. Bu adımdan sonra her özelliğin ortalaması 0, standart sapması 1 olur. Böylece bir derece sıcaklık ile bir mikrogram partikül uzaklıklarda artık farklı ağırlık taşımaz. Hücre üç özelliğin μ ve σ değerlerini yazdırır.⟫""", "sec-3")
    code(src(core.standardize) + """


CLUSTER_FEATURES = """ + repr(core.CLUSTER_FEATURES) + """
X = anom[CLUSTER_FEATURES].to_numpy()
Z, mu, sd = standardize(X)
print("μ =", mu.round(3), "  σ =", sd.round(3))""", "s3-std")
    md("""### 3.2 ⟪k-means with k = 4‖k = 4 ile k-ortalamalar⟫

⟪k-means places k centers in the standardized space and repeats two steps until nothing changes [5]. First, every minute is assigned to its nearest center. Then every center moves to the mean of the minutes assigned to it. The cell runs `KMeans` of scikit-learn with four groups and ten random starts and keeps the best result. It numbers the groups from the coolest to the warmest center and converts the centers back to sensor units. The cross table then counts which point types fill each group. The 3D plot shows the same cloud as the workshop site and can be rotated with the mouse.‖k-ortalamalar, standartlaştırılmış uzaya k merkez yerleştirir ve hiçbir şey değişmeyene kadar iki adımı tekrarlar [5]. Önce her dakika en yakın merkeze atanır. Ardından her merkez kendisine atanan dakikaların ortalamasına taşınır. Hücre scikit-learn kütüphanesindeki `KMeans` sınıfını dört grup ve on rastgele başlangıçla çalıştırır ve en iyi sonucu tutar. Grupları en serin merkezden en sıcak merkeze doğru numaralandırır ve merkezleri sensör birimlerine geri çevirir. Çapraz tablo ardından her grubu hangi nokta türlerinin doldurduğunu sayar. 3B grafik, atölye sitesindekiyle aynı bulutu gösterir ve fareyle döndürülebilir.⟫""", "s3-km-md")
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
    md("""### 3.3 ⟪How many groups?‖Kaç grup?⟫

⟪k-means needs the number of groups in advance. The cell runs it for every k from 2 to 6 and records two scores. J, the total squared distance of the minutes from their centers, always falls when k grows, because more centers lie closer to the minutes, so J alone cannot choose k. The silhouette compares, for each minute, the mean distance to its own group with the mean distance to the nearest other group, on a scale from −1 to +1 [6]. A higher silhouette means better separated groups. When several values of k score almost the same, the choice is a decision of the analyst that has to be explained. This notebook works with four groups, which can be read as four kinds of microclimate.‖k-ortalamalar grup sayısının önceden verilmesini ister. Hücre algoritmayı 2'den 6'ya kadar her k için çalıştırır ve iki skor kaydeder. Dakikaların merkezlerine toplam kare uzaklığı olan J, k büyüdükçe her zaman düşer, çünkü merkez sayısı arttıkça merkezler dakikalara yaklaşır. Bu yüzden k değerini tek başına J seçemez. Siluet ise her dakika için kendi grubuna ortalama uzaklığı, en yakın diğer gruba ortalama uzaklıkla −1 ile +1 arasındaki bir ölçekte karşılaştırır [6]. Daha yüksek bir siluet değeri, birbirinden daha iyi ayrılmış gruplar anlamına gelir. Birkaç k değeri neredeyse aynı skoru aldığında seçim, analistin gerekçelendirmesi gereken bir karardır. Bu defter, dört tür mikroiklim olarak okunabilen dört grupla çalışmaktadır.⟫""", "s3-k-md")
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
    md("""### 3.4 ⟪Principal component analysis‖Temel bileşenler analizi⟫

⟪Principal component analysis (PCA) turns several standardized channels into new axes, the principal components, ordered by how much of the variation they keep [7]. Each component is a weighted sum of the channels, and its weights are called loadings. The cell standardizes six channels: The temperature, PM2.5 and CO₂ differences, the relative humidity, the logarithm of the light level and the UVA irradiance. A minute without a CO₂ value is placed at the median of its campus and round, that is, its CO₂ difference is set to zero. The cell prints the share of the variation kept by each of the first three components, which together keep about 86 %, and the table of loadings. A large loading, positive or negative, shows which channels a component mainly describes. The 3D plot finally draws the minutes on the three new axes, colored by point type.‖Temel bileşenler analizi (PCA), standartlaştırılmış birkaç kanalı, koruduğu değişim miktarına göre sıralanan yeni eksenlere, yani temel bileşenlere dönüştürür [7]. Her bileşen kanalların ağırlıklı bir toplamıdır ve bu ağırlıklara yük denir. Hücre altı kanalı standartlaştırır: Sıcaklık, PM2,5 ve CO₂ farkları, bağıl nem, ışık şiddetinin logaritması ve UVA ışınımı. CO₂ değeri olmayan bir dakika kendi kampüsünün ve turunun medyanına yerleştirilir, yani CO₂ farkı sıfır kabul edilir. Hücre ilk üç bileşenin her birinin koruduğu değişim payını ve yük tablosunu yazdırır. Üç bileşen birlikte değişimin yaklaşık %86'sını korur. Pozitif ya da negatif büyük bir yük, bir bileşenin esas olarak hangi kanalları anlattığını gösterir. 3B grafik son olarak dakikaları bu üç yeni eksende nokta türüne göre renklendirerek çizer.⟫""", "s3-pca-md")
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

⟪Section 4 trains a random forest that predicts the PM2.5 of each clean minute [8]. It tests the model in three ways, asks which inputs the model relies on and shows its answer with sliders, partial dependence and a 3D surface.‖Defterin 4. kısmı, her temiz dakikanın PM2,5 değerini tahmin eden bir rastgele orman eğitir [8]. Modeli üç farklı biçimde test eder, hangi girdilere dayandığını sorar ve cevabını kaydırıcılar, kısmi bağımlılık ve bir 3B yüzeyle gösterir.⟫

### 4.1 ⟪The model table‖Model tablosu⟫

⟪The function `model_table` joins every clean minute with the field form of its visit and builds the eight inputs of the model. The vehicles and people counted in 15 minutes become rates per minute. The sun condition becomes a number: 0 for shade, 0.5 for partial sun and 1 for full sun. The background PM2.5 of a morning is the median PM2.5 at the reference point of that campus and round. Temperature, relative humidity and the hour come from the minute itself. The target is the corrected PM2.5 of the minute. The cell prints how many minutes and measurement points the table contains.‖`model_table` fonksiyonu her temiz dakikayı kendi ziyaretinin saha formuyla birleştirir ve modelin sekiz girdisini oluşturur. 15 dakikada sayılan araç ve kişi sayıları dakika başına orana çevrilir. Güneş durumu bir sayıya dönüştürülür: Gölge için 0, kısmi güneş için 0,5 ve tam güneş için 1. Bir sabahın arka plan PM2,5 değeri, o kampüs ve turda referans noktasında ölçülen PM2,5 değerlerinin medyanıdır. Sıcaklık, bağıl nem ve saat dakikanın kendisinden gelir. Hedef değişken, dakikanın düzeltilmiş PM2,5 değeridir. Hücre tablodaki dakika ve ölçüm noktası sayısını yazdırır.⟫""", "sec-4")
    code(src(core.model_table) + """


MODEL_FEATURES = """ + wrap_list(core.MODEL_FEATURES, width=64) + """
table = model_table(minutes, forms).dropna(subset=MODEL_FEATURES + ["pm25_ugm3"])
Xm = table[MODEL_FEATURES].to_numpy()
y = table["pm25_ugm3"].to_numpy()
groups = (table.campus + table.point_id).to_numpy()
print(len(y), "⟪minutes from‖dakika,⟫", len(set(groups)), "⟪measurement points‖ölçüm noktası⟫")
display(table[MODEL_FEATURES + ["pm25_ugm3"]].head(3))""", "s4-table")
    md("""### 4.2 ⟪Three scores‖Üç skor⟫

⟪The coefficient of determination R² compares the errors of the model with the spread of the data:‖Belirlilik katsayısı R², modelin hatalarını verinin yayılımıyla karşılaştırır:⟫

$$R^2 = 1 - \\frac{\\sum_i (y_i - \\hat{y}_i)^2}{\\sum_i (y_i - \\bar{y})^2}$$

⟪Here y<sub>i</sub> is the measured PM2.5 of minute i, ŷ<sub>i</sub> the prediction of the model and ȳ the mean of all measurements. R² = 1 means perfect predictions, and R² = 0 means that the model is no better than always predicting the mean. The forest has 40 trees with at most six levels each. The cell computes three scores. The first is measured on the training minutes themselves and is always too optimistic. The second comes from five-fold cross-validation over random minutes, where minutes of the same visit can sit in both the training and the test part. The third leaves one measurement point out at a time, so the model never sees the point on which it is tested. Many minutes from one point are not independent observations, which is why only the third score tells how the model would do at a new place [9].‖Burada y<sub>i</sub>, i. dakikada ölçülen PM2,5 değeri, ŷ<sub>i</sub> modelin tahmini, ȳ ise bütün ölçümlerin ortalamasıdır. R² = 1 kusursuz tahmin anlamına gelir. R² = 0 ise modelin her seferinde ortalamayı tahmin etmekten daha iyi olmadığını gösterir. Orman, her biri en çok altı düzey derinliğinde 40 ağaçtan oluşmaktadır. Hücre üç skor hesaplar. İlki eğitim dakikalarının kendisi üzerinde ölçülür ve her zaman fazla iyimserdir. İkincisi rastgele dakikalar üzerinde beş katlı çapraz doğrulamadan gelir. Bu durumda aynı ziyaretin dakikaları hem eğitim hem de test kısmında bulunabilir. Üçüncüsü her seferinde bir ölçüm noktasını dışarıda bırakır, böylece model test edildiği noktayı hiç görmez. Aynı noktadan gelen çok sayıda dakika birbirinden bağımsız gözlemler değildir. Bu yüzden modelin yeni bir yerde nasıl çalışacağını yalnızca üçüncü skor anlatır [9].⟫""", "s4-cv-md")
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

⟪Permutation importance asks how much worse the model becomes when one input is made useless. The values of that input are shuffled among the minutes, which breaks its link with PM2.5, and the drop of R² is measured. To keep the test honest, the forest is trained on two campuses and the importances are measured on the third. This is repeated for each campus, and the three results are averaged. The bar chart shows the mean drop of R² for each input. A large drop means that the model relies on that input, but it does not prove that the input causes PM2.5 in the real world.‖Permütasyon önemi, bir girdi işe yaramaz hâle getirildiğinde modelin ne kadar kötüleştiğini sorar. O girdinin değerleri dakikalar arasında karıştırılır, böylece girdinin PM2,5 ile bağı koparılır ve R² değerindeki düşüş ölçülür. Testin dürüst kalması için orman iki kampüste eğitilir ve önem değerleri üçüncü kampüste ölçülür. Bu işlem her kampüs için tekrarlanır ve üç sonucun ortalaması alınır. Çubuk grafik her girdi için R² değerindeki ortalama düşüşü gösterir. Büyük bir düşüş, modelin o girdiye dayandığını gösterir. Ancak bu, o girdinin gerçek dünyada PM2,5'e neden olduğunu kanıtlamaz.⟫""", "s4-imp-md")
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

⟪The sliders change the inputs of the trained forest, and the title of the plot gives its prediction. Every slider starts at the median of its input and stays within the range of the measured data, because a forest cannot predict beyond what it has seen. Each bar shows how much the prediction would change if that one input went back to its median while the others kept their slider values. Bars to the right show inputs that push the prediction up, and bars to the left show inputs that pull it down.‖Kaydırıcılar eğitilmiş ormanın girdilerini değiştirir, grafiğin başlığı da modelin tahminini verir. Her kaydırıcı kendi girdisinin medyanından başlar ve ölçülen verinin aralığında kalır, çünkü bir orman gördüğünün ötesini tahmin edemez. Her çubuk, yalnızca o girdi medyanına dönseydi ve diğerleri kaydırıcı değerlerinde kalsaydı tahminin ne kadar değişeceğini gösterir. Sağa uzanan çubuklar tahmini yukarı iten, sola uzananlar ise aşağı çeken girdileri gösterir.⟫""", "s4-wi-md")
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

⟪Partial dependence shows the average answer of the model as one input changes [10]:‖Kısmi bağımlılık, bir girdi değişirken modelin ortalama cevabını gösterir [10]:⟫

$$\\hat{f}_S(x_S) = \\frac{1}{n}\\sum_{i=1}^{n} \\hat{f}\\bigl(x_S, \\mathbf{x}_C^{(i)}\\bigr)$$

⟪Here x<sub>S</sub> is the input being studied, **x**<sub>C</sub><sup>(i)</sup> are the other inputs of minute i and n is the number of minutes. For each value of x<sub>S</sub>, the model predicts all minutes with x<sub>S</sub> set to that value and averages the predictions. The cell draws the curves for vehicles per minute, background PM2.5, people per minute and green cover. With `kind="both"`, thin lines show 60 sampled minutes and the thick line their average, so the plot also shows how far single minutes stray from the average answer.‖Burada x<sub>S</sub> incelenen girdi, **x**<sub>C</sub><sup>(i)</sup> i. dakikanın diğer girdileri, n ise dakika sayısıdır. x<sub>S</sub> girdisinin her değeri için model, bütün dakikaları x<sub>S</sub> bu değere eşitlenmiş olarak tahmin eder ve tahminlerin ortalamasını alır. Hücre dakikadaki araç sayısı, arka plan PM2,5 değeri, dakikadaki kişi sayısı ve yeşil örtü için eğrileri çizer. `kind="both"` ayarıyla ince çizgiler örneklenen 60 dakikayı, kalın çizgi ise bunların ortalamasını gösterir. Böylece grafik tek tek dakikaların ortalama cevaptan ne kadar ayrıldığını da gösterir.⟫""", "s4-pdp-md")
    code("""from sklearn.inspection import PartialDependenceDisplay

fig, ax = plt.subplots(figsize=(12, 3.2))
PartialDependenceDisplay.from_estimator(
    forest, Xm, features=[0, 7, 1, 2], feature_names=MODEL_FEATURES, ax=ax,
    kind="both", subsample=60, random_state=RANDOM_STATE)
plt.tight_layout(); plt.show()""", "s4-pdp")
    md("""### 4.6 ⟪The model surface in 3D‖Model yüzeyi 3B⟫

⟪The last cell evaluates the forest on a grid of 30 × 30 combinations of vehicles per minute and background PM2.5, while the other six inputs stay at their medians. The result is drawn as a surface that can be rotated with the mouse. The surface rises in steps rather than smoothly, because every tree splits its inputs at threshold values.‖Son hücre ormanı, dakikadaki araç sayısı ile arka plan PM2,5 değerinin 30 × 30'luk bir ızgarasında değerlendirir. Bu sırada diğer altı girdi medyanlarında kalır. Sonuç, fareyle döndürülebilen bir yüzey olarak çizilir. Yüzey düzgün bir biçimde değil, basamaklar hâlinde yükselir, çünkü her ağaç girdilerini belirli eşik değerlerinden böler.⟫""", "s4-surf-md")
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

⟪Section 5 prepares the results for a report. It builds a fact table from the analysis and writes a prompt that hands these facts to an AI assistant. It then checks every number of an AI-written text against the table and prints a solution card for the workshop of 28 November.‖Defterin 5. kısmı sonuçları bir rapora hazırlar. Analizden bir olgu tablosu oluşturur, bu olguları bir YZ asistanına veren bir istem yazar, YZ ile yazılmış bir metindeki her sayıyı tabloyla denetler ve 28 Kasım çalıştayı için bir çözüm kartı yazdırır.⟫

### 5.1 ⟪The fact table‖Olgu tablosu⟫

⟪The fact table gathers the numbers that a report may use. For the campus set in `CAMPUS`, it lists PM2.5, temperature and CO₂ for every point type: The visit medians of both rounds, their mean and the difference from the reference point. The table is rounded to one decimal and saved as a CSV file, so that it can be attached to a report or pasted into an assistant.‖Olgu tablosu, bir raporun kullanabileceği sayıları bir araya getirir. `CAMPUS` değişkeninde belirtilen kampüs için her nokta türünde PM2,5, sıcaklık ve CO₂ değerlerini verir: İki turun ziyaret medyanları, bunların ortalaması ve referans noktasından fark. Tablo bir ondalık basamağa yuvarlanır ve bir CSV dosyası olarak kaydedilir. Böylece bir rapora eklenebilir ya da bir asistana yapıştırılabilir.⟫""", "sec-5")
    code("""CAMPUS = "B"
facts = pd.concat([fair_table(visits, ch).assign(channel=ch)
                   for ch in ["pm25_ugm3", "temperature_c", "co2_ppm"]])
facts = facts[facts.campus == CAMPUS][["channel", "point_type", "round1", "round2",
                                       "two_round_mean", "minus_reference"]].round(1)
facts.to_csv(f"nokta_facts_{CAMPUS}.csv", index=False)
display(facts)""", "s5-facts")
    md("""### 5.2 ⟪A safe prompt‖Güvenli bir istem⟫

⟪A safe prompt does not ask the assistant to know the numbers. It hands the numbers over, names the task and writes the rules down. The function `make_prompt` combines a role, a task, the fact table and the seven rules in `RULES`. The rules forbid rankings of campuses and comparisons with 24-hour or annual guidelines. They also ask for the averaging time of every value, keep observation, interpretation and advice apart and call for cautious verbs when causes are discussed. The printed prompt can be copied into any assistant, and a team can extend the rules for its own report.‖Güvenli bir istem, asistandan sayıları bilmesini istemez. Sayıları ona verir, görevi tanımlar ve kuralları yazılı olarak belirtir. `make_prompt` fonksiyonu bir rolü, bir görevi, olgu tablosunu ve `RULES` listesindeki yedi kuralı birleştirir. Kurallar kampüslerin sıralanmasını ve değerlerin 24 saatlik ya da yıllık kılavuzlarla karşılaştırılmasını yasaklar. Ayrıca her değerin ortalama alma süresinin belirtilmesini, gözlemin, yorumun ve önerinin birbirinden ayrılmasını ve nedenler tartışılırken temkinli ifadeler kullanılmasını ister. Yazdırılan istem herhangi bir asistana kopyalanabilir, bir ekip de kuralları kendi raporu için genişletebilir.⟫""", "s5-prompt-md")
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

⟪The auditor reads a text, lists every number in it and marks each number that does not appear in the fact table. A number counts as supported when it lies within 0.05 of a value in the table, which allows for rounding. The sample text in `text` repeats some errors of Part 5 of the workshop site, and an AI-written text of your own can be pasted in its place. A flagged number is not always wrong, for example a guideline value or a year, but every flagged number needs a source.‖Denetleyici bir metni okur, içindeki her sayıyı listeler ve olgu tablosunda bulunmayan sayıları işaretler. Bir sayı, tablodaki bir değere 0,05'ten daha yakınsa desteklenmiş sayılır. Bu pay, yuvarlamadan doğan farkları karşılar. `text` değişkenindeki örnek metin, atölye sitesinin 5. Bölümündeki bazı hataları tekrarlar. Bunun yerine YZ ile yazılmış kendi metninizi de yapıştırabilirsiniz. İşaretli bir sayı her zaman yanlış değildir, örneğin bir kılavuz değeri ya da bir yıl olabilir. Ancak işaretli her sayının bir kaynağı olmalıdır.⟫""", "s5-audit-md")
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
    md("""### 5.4 ⟪The solution card‖Çözüm kartı⟫

⟪On 28 November the NOKTA National Environment Workshop works at three thematic tables. Every proposal brought there answers five questions: The problem, the evidence, the solution, its feasibility and the role of young people. The function `solution_card` writes these five answers as a card. The example starts from the sunny concrete square of the fact table and takes its evidence, the difference from the reference point, directly from the analysis. A team replaces the other four answers with its own words.‖28 Kasım'da NOKTA Ulusal Çevre Çalıştayı üç tematik masada çalışır ve oraya getirilen her öneri beş soruyu cevaplar: Sorun, dayanak, çözüm, uygulanabilirlik ve gençlerin rolü. `solution_card` fonksiyonu bu beş cevabı bir kart olarak yazar. Örnek, olgu tablosundaki güneşli beton meydandan başlar ve dayanağını, yani referans noktasından farkı, doğrudan analizden alır. Bir ekip diğer dört cevabı kendi cümleleriyle değiştirir.⟫""", "s5-card-md")
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

⟪Each challenge below continues the analysis from the point of view of one field of study. It starts from the tables of this notebook and adds a small piece of field work or a calculation.‖Aşağıdaki her görev, analizi bir alanın bakış açısından sürdürür. Görev bu defterdeki tablolardan başlar ve bunlara küçük bir saha çalışması ya da bir hesap ekler.⟫

| ⟪Field‖Alan⟫ | ⟪Challenge‖Görev⟫ |
|---|---|
| ⟪Engineering‖Mühendislik⟫ | ⟪Design a test that separates real heat at the sunny square from sunshine on the sensor housing.‖Güneşli meydandaki gerçek sıcaklığı sensör gövdesine vuran güneşten ayıran bir test tasarlayın.⟫ |
| ⟪Health sciences‖Sağlık bilimleri⟫ | ⟪Estimate how long a student waits at the bus stop each day and what the PM2.5 difference means for that time.‖Bir öğrencinin her gün otobüs durağında ne kadar beklediğini ve PM2,5 farkının bu süre için ne anlama geldiğini kestirin.⟫ |
| ⟪Social sciences‖Sosyal bilimler⟫ | ⟪Ask ten students where on campus they feel the air is worst and compare their answers with the fair table.‖On öğrenciye kampüste havayı en kötü nerede hissettiklerini sorun ve cevaplarını adil tabloyla karşılaştırın.⟫ |
| ⟪Communication‖İletişim⟫ | ⟪Turn one result into a figure for the congress that shows its averaging time and its uncertainty.‖Bir sonucu ortalama alma süresini ve belirsizliğini gösteren bir kongre şekline dönüştürün.⟫ |
| ⟪Economics and management‖İktisat ve işletme⟫ | ⟪Compare the cost per degree of shade sails and trees for the sunny square over ten years.‖Güneşli meydan için gölgelik ve ağaçların on yıllık derece başına maliyetini karşılaştırın.⟫ |
| ⟪Education‖Eğitim⟫ | ⟪Plan a 40-minute lesson in which pupils repeat the two-round design with a thermometer.‖Öğrencilerin iki turlu tasarımı bir termometreyle tekrarladığı 40 dakikalık bir ders planlayın.⟫ |""", "challenges")
    md("""## ⟪After the notebook‖Defterden sonra⟫

⟪Open the [debrief of the NOKTA Lab](""" + SITE + """lab.html#debrief) for a field report of the session. For the analysis days of 21 to 24 November, set `DATA_SOURCE = "own"` in Section 0 and run the notebook on your own NOKTA files.‖Oturumun saha raporu için [NOKTA Laboratuvarının değerlendirmesini](""" + SITE + """tr/lab.html#debrief) açın. 21-24 Kasım analiz günleri için 0. kısımda `DATA_SOURCE = "own"` ayarını yapın ve defteri kendi NOKTA dosyalarınızla çalıştırın.⟫

**⟪References‖Kaynaklar⟫**

1. Leys, C., Ley, C., Klein, O., Bernard, P., & Licata, L. (2013). Detecting outliers: Do not use standard deviation around the mean, use absolute deviation around the median. *Journal of Experimental Social Psychology, 49*(4), 764–766. https://doi.org/10.1016/j.jesp.2013.03.013
2. Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008). Isolation forest. In *Proceedings of the 8th IEEE International Conference on Data Mining (ICDM 2008)* (pp. 413–422). IEEE. https://doi.org/10.1109/ICDM.2008.17
3. Crilley, L. R., Shaw, M., Pound, R., Kramer, L. J., Price, R., Young, S., Lewis, A. C., & Pope, F. D. (2018). Evaluation of a low-cost optical particle counter (Alphasense OPC-N2) for ambient air monitoring. *Atmospheric Measurement Techniques, 11*(2), 709–720. https://doi.org/10.5194/amt-11-709-2018
4. Alduchov, O. A., & Eskridge, R. E. (1996). Improved Magnus form approximation of saturation vapor pressure. *Journal of Applied Meteorology, 35*(4), 601–609. https://doi.org/10.1175/1520-0450(1996)035<0601:IMFAOS>2.0.CO;2
5. Lloyd, S. P. (1982). Least squares quantization in PCM. *IEEE Transactions on Information Theory, 28*(2), 129–137. https://doi.org/10.1109/TIT.1982.1056489
6. Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. *Journal of Computational and Applied Mathematics, 20*, 53–65. https://doi.org/10.1016/0377-0427(87)90125-7
7. Jolliffe, I. T., & Cadima, J. (2016). Principal component analysis: A review and recent developments. *Philosophical Transactions of the Royal Society A, 374*(2065), 20150202. https://doi.org/10.1098/rsta.2015.0202
8. Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5–32. https://doi.org/10.1023/A:1010933404324
9. Roberts, D. R., Bahn, V., Ciuti, S., Boyce, M. S., Elith, J., Guillera-Arroita, G., Hauenstein, S., Lahoz-Monfort, J. J., Schröder, B., Thuiller, W., Warton, D. I., Wintle, B. A., Hartig, F., & Dormann, C. F. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*(8), 913–929. https://doi.org/10.1111/ecog.02881
10. Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. *The Annals of Statistics, 29*(5), 1189–1232. https://doi.org/10.1214/aos/1013203451""", "after")
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
