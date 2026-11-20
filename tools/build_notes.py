"""Build printable workshop notes (Word and PDF) in English and Turkish.

The notes follow the pages of the site: the same headings, questions, answers,
formulas with their worked examples, takeaways and references. Formulas are
typeset with pdflatex and placed as images. The Word files serve as source
text (for example for NotebookLM); the PDF files go into notes/ of the
repository.

Run after tools/build_site.py:
    python tools/build_notes.py [--word-dir DIR]
"""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

from bs4 import BeautifulSoup
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

import build_site as bs

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["index", "part1", "part2", "part3", "part4", "part5", "lab"]
TITLE = {"en": "AI-Based Environmental Data Analysis and Interpretation",
         "tr": "Yapay Zekâ ile Çevresel Veri Analizi ve Yorumlama"}
SUB = {"en": "Workshop notes · NOKTA, Objective Measurement, Participation, Monitoring and Action Network · ÜNİDES 2026",
       "tr": "Atölye notları · NOKTA, Nesnel Ölçüm, Katılım, Takip ve Aksiyon Ağı · ÜNİDES 2026"}
FILES = {"en": "NOKTA_Workshop_Notes_EN", "tr": "NOKTA_Atolye_Notlari_TR"}
GREEN = RGBColor(0x0E, 0x7A, 0x5F)
INK = RGBColor(0x18, 0x23, 0x1F)
MUTED = RGBColor(0x56, 0x64, 0x5D)


def tex_png(tex, cache):
    key = hashlib.md5(tex.encode()).hexdigest()[:12]
    png = cache / f"{key}.png"
    if png.exists():
        return png
    doc = (r"\documentclass[border=4pt,12pt]{standalone}\usepackage{amsmath,amssymb}"
           r"\usepackage[utf8]{inputenc}\usepackage[T1]{fontenc}"
           r"\begin{document}$\displaystyle " + tex + r"$\end{document}")
    texf = cache / f"{key}.tex"
    texf.write_text(doc, encoding="utf-8")
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", texf.name],
                   cwd=cache, check=True, capture_output=True)
    subprocess.run(["pdftoppm", "-png", "-r", "300", "-singlefile", f"{key}.pdf", key],
                   cwd=cache, check=True, capture_output=True)
    return png


def text_of(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)).replace(" .", ".").replace(" ,", ",")


def add_par(doc, text, size=11, color=INK, bold=False, italic=False, space=6, style=None):
    p = doc.add_paragraph(style=style)
    run = p.add_run(text)
    run.font.size = Pt(size); run.font.color.rgb = color; run.bold = bold; run.italic = italic
    p.paragraph_format.space_after = Pt(space)
    return p


def add_rich(doc, el, size=11, color=INK, prefix=None):
    """Paragraph that keeps bold text and sub/superscripts."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    if prefix:
        r = p.add_run(prefix); r.bold = True; r.font.size = Pt(size); r.font.color.rgb = GREEN
    def walk(node, bold=False, sub=False, sup=False):
        for ch in node.children:
            if isinstance(ch, str):
                t = re.sub(r"\s+", " ", ch)
                if t:
                    r = p.add_run(t); r.bold = bold; r.font.size = Pt(size); r.font.color.rgb = color
                    r.font.subscript = sub; r.font.superscript = sup
            elif ch.name in ("b", "strong"):
                walk(ch, True, sub, sup)
            elif ch.name == "sub":
                walk(ch, bold, True, sup)
            elif ch.name == "sup":
                walk(ch, bold, sub, True)
            elif ch.name in ("script", "style"):
                continue
            elif ch.name == "br":
                r = p.add_run(); r.add_break()
            else:
                walk(ch, bold, sub, sup)
    walk(el)
    return p


def page_soup(page, lang, data, extra):
    src = (bs.SRC / f"{page}.html").read_text(encoding="utf-8")
    body = src[re.match(r"<!--META(.*?)-->", src, re.S).end():]
    text = bs.fill_numbers(bs.lang_pick(body, lang), data, extra, lang)
    text = (text.replace("{{COLAB}}", bs.COLAB[lang]).replace("{{SITE}}", bs.SITE)
            .replace("{{REPO}}", f"https://github.com/{bs.OWNER}/{bs.REPO}"))
    text = re.sub(r"<script>.*?</script>", "", text, flags=re.S)
    return BeautifulSoup(text, "html.parser")


def build(word_dir):
    data = bs.load_data()
    extra = bs.worked_examples(data)
    cache = Path(tempfile.mkdtemp())
    (ROOT / "notes").mkdir(exist_ok=True)
    word_dir.mkdir(parents=True, exist_ok=True)
    for lang in ("en", "tr"):
        doc = Document()
        sec = doc.sections[0]
        sec.left_margin = sec.right_margin = Cm(2.2); sec.top_margin = sec.bottom_margin = Cm(2.0)
        st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11)
        h = add_par(doc, TITLE[lang], size=22, color=INK, bold=True, space=4)
        add_par(doc, SUB[lang], size=12, color=MUTED, space=10)
        ident = ("Prof. Dr. Utku Köse · Süleyman Demirel University, AI Application and Research Center (YAZEM) · "
                 "University of North Dakota · Universidad Panamericana · Vel Tech University"
                 if lang == "en" else
                 "Prof. Dr. Utku Köse · Süleyman Demirel Üniversitesi, Yapay Zekâ Uygulama ve Araştırma Merkezi (YAZEM) · "
                 "University of North Dakota · Universidad Panamericana · Vel Tech University")
        add_par(doc, ident, size=10, color=MUTED, space=2)
        add_par(doc, ("Workshop site: " if lang == "en" else "Atölye sitesi: ") + bs.SITE + ("" if lang == "en" else "tr/"),
                size=10, color=MUTED, space=2)
        add_par(doc, ("This workshop is updated in line with current developments in the field. First version: November 2026."
                      if lang == "en" else
                      "Bu atölye alandaki güncel gelişmelere göre güncellenmektedir. İlk sürüm: Kasım 2026."),
                size=10, color=MUTED, italic=True, space=12)
        intro = ("These notes follow the pages of the workshop site in order. Each part lists the question asked before the reveal, "
                 "the answer, the formulas with the meaning of their symbols and a worked example, and the takeaway. "
                 "The data are synthetic and describe no real campus."
                 if lang == "en" else
                 "Bu notlar atölye sitesinin sayfalarını sırasıyla izlemektedir. Her bölümde sonuç gösterilmeden önce sorulan soru, "
                 "cevabı, sembollerin anlamı ve çözümlü bir örnekle birlikte formüller ve çıkarım yer almaktadır. "
                 "Veriler sentetiktir ve gerçek bir kampüsü anlatmaz.")
        add_par(doc, intro, space=12)
        for page in PAGES:
            soup = page_soup(page, lang, data, extra)
            for block in soup.find_all(["section"], recursive=True):
                cls = block.get("class") or []
                if "parthead" in cls or "hero" in cls:
                    k = block.find(class_="kicker")
                    if k: add_par(doc, text_of(k).upper(), size=9, color=GREEN, bold=True, space=2)
                    t = block.find("h1")
                    if t: doc.add_heading(text_of(t), level=1)
                    for lead in block.find_all(class_=["lead", "sub"]):
                        add_par(doc, text_of(lead), size=12, color=MUTED, space=8)
                    continue
                if block.get("id") == "refs":
                    doc.add_heading("References" if lang == "en" else "Kaynaklar", level=3)
                    for li in block.find_all("li"):
                        add_par(doc, text_of(li), size=9, color=MUTED, space=3)
                    continue
                stations = block.find_all(class_="station") if "scrolly" in cls else ([block] if "station" in cls else [])
                if "section" in cls and page == "index":
                    for el in block.find_all(["h2", "p", "table"]):
                        if el.name == "h2":
                            doc.add_heading(text_of(el), level=2)
                        elif el.name == "p" and el.find_parent(class_="pcard") is None and el.find_parent(class_="nbref") is None:
                            add_rich(doc, el, size=11 if "note" not in (el.get("class") or []) else 9.5,
                                     color=INK if "note" not in (el.get("class") or []) else MUTED)
                    for card in block.find_all(class_="pcard"):
                        t = card.find("h3"); tm = card.find(class_="t"); pp = card.find("p")
                        add_par(doc, f"{text_of(tm)} · {text_of(t)}", bold=True, space=2)
                        add_par(doc, text_of(pp), color=MUTED, space=6)
                for stn in stations:
                    head = stn.find(class_="station-head")
                    if head:
                        doc.add_heading(text_of(head), level=2)
                    for el in stn.find_all(True, recursive=True):
                        c = el.get("class") or []
                        if el.find_parent(class_="formula") is not None and "formula" not in c:
                            continue
                        if "poll" in c:
                            q = el.find(class_="q")
                            add_par(doc, (("Question: " if lang == "en" else "Soru: ") + text_of(q)), bold=True, space=3)
                            ans = el.find(class_="msg-right") or el.find(class_="msg-wrong")
                            if ans:
                                add_par(doc, ("Answer: " if lang == "en" else "Cevap: ") + text_of(ans), color=MUTED, space=8)
                        elif "formula" in c:
                            for t in el.find_all(["texd", "tex"]):
                                png = tex_png(t.get_text(), cache)
                                pic = doc.add_paragraph(); pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
                                px = __import__("PIL.Image", fromlist=["Image"]).open(png).size[0]
                                w = min(13.5, px * 2.54 / 300 * 0.95)
                                pic.add_run().add_picture(str(png), width=Cm(w))
                            sym = el.find(class_="sym")
                            if sym: add_rich(doc, sym, size=10, color=MUTED)
                            wk = el.find(class_="worked")
                            if wk: add_rich(doc, wk, size=10.5)
                        elif "takeaway" in c or "everyday" in c:
                            add_rich(doc, el, size=11)
                        elif el.name == "p" and not el.find_parent(class_=["poll", "nbref", "formula", "takeaway", "everyday", "hud", "legend3d"]) \
                                and "cap" not in c and el.get("id") is None:
                            if text_of(el):
                                add_rich(doc, el, size=10 if "note" in c else 11, color=MUTED if "note" in c else INK)
                        elif "nbref" in c:
                            pp = el.find("p")
                            add_par(doc, "Colab: " + text_of(pp), size=10, color=GREEN, space=8)
        doc.add_heading("Human-AI collaboration" if lang == "en" else "İnsan-yapay zekâ işbirliği", level=2)
        add_par(doc, ("This workshop was developed through human-AI collaboration. Human intellectual knowledge and expertise "
                      "are the fundamental starting point of the workshop. The author guides and supervises every stage of its "
                      "development. The final version is presented only after the author's review and approval."
                      if lang == "en" else
                      "Bu atölye insan-yapay zekâ işbirliğiyle geliştirilmiştir. İnsanın entelektüel birikimi ve uzmanlığı atölyenin "
                      "temel çıkış noktasıdır. Yazar, geliştirmenin her aşamasını yönlendirmekte ve denetlemektedir. Nihai hâl, "
                      "ancak yazarın incelemesi ve onayından sonra sunulmaktadır."))
        sig = doc.add_paragraph(); sig.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = sig.add_run("Prof. Dr. Utku Köse\n"); r.bold = True
        r2 = sig.add_run("Süleyman Demirel University · University of North Dakota · Universidad Panamericana · Vel Tech University\n"
                         "utkukose.com · ORCID 0000-0002-9652-6415 · github.com/utkukose\n"
                         + ("NOKTA workshop · ÜNİDES 2026 · First version: November 2026"
                            if lang == "en" else "NOKTA atölyesi · ÜNİDES 2026 · İlk sürüm: Kasım 2026"))
        r2.font.size = Pt(9); r2.font.color.rgb = MUTED
        out = word_dir / f"{FILES[lang]}.docx"
        doc.save(out)
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(ROOT / "notes"), str(out)],
                       check=True, capture_output=True)
        print("written", out.name, "and notes/" + FILES[lang] + ".pdf")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--word-dir", default=str(ROOT.parent / "word_notes"))
    build(Path(ap.parse_args().word_dir))
