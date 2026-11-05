"""Builds CV_Hideki_Harada_{EN,ES}.tex and .docx in files/ from _pages/cv.md and _pages/es/cv.md.
Run: uv run --with python-docx python scripts/make_cv_formats.py"""
import re, pathlib
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://haradaoyakawahideki.github.io"
NAVY = RGBColor(0x00, 0x3A, 0x70)
HEAD = {"en": "Political scientist · Education and public policy · Lima, Peru",
        "es": "Politólogo · Educación y políticas públicas · Lima, Perú"}
CONTACT = [("harada.oyakawa.hideki@gmail.com", "mailto:harada.oyakawa.hideki@gmail.com"),
           ("haradaoyakawahideki.github.io", SITE),
           ("linkedin.com/in/hideki-harada", "https://www.linkedin.com/in/hideki-harada"),
           ("github.com/haradaoyakawahideki", "https://github.com/haradaoyakawahideki")]

def parse(src):
    md = (ROOT / src).read_text()
    md = re.sub(r"^---.*?---\s*", "", md, flags=re.S)
    md = re.sub(r"(?m)^<(a|small)[^\n]*\n", "", md)          # drop download buttons/links
    blocks = []                                              # (kind, level, text)
    for line in md.splitlines():
        if not line.strip(): continue
        if line.startswith("## "): blocks.append(("h", 0, line[3:].strip()))
        elif re.match(r"^\s{2,}- ", line): blocks.append(("li", 1, line.strip()[2:]))
        elif line.startswith("- "): blocks.append(("li", 0, line[2:]))
        else: blocks.append(("p", 0, line.strip()))
    return blocks

TOKEN = re.compile(r"(\*\*.+?\*\*|\*.+?\*|<em>.+?</em>|\[[^\]]+\]\([^)]+\))")
def runs(text):
    for part in TOKEN.split(text):
        if not part: continue
        if part.startswith("**"): yield ("b", part[2:-2], None)
        elif part.startswith("<em>"): yield ("i", part[4:-5], None)
        elif part.startswith("*"): yield ("i", part[1:-1], None)
        elif part.startswith("["):
            t, u = re.match(r"\[([^\]]+)\]\(([^)]+)\)", part).groups()
            yield ("a", t, SITE + u if u.startswith("/") else u)
        else: yield ("t", part, None)

# ---------- LaTeX ----------
def tex_escape(s):
    rep = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
           "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(rep.get(c, c) for c in s)
def tex_inline(text):
    text = re.sub(r'"([^"]+)"', "``\\1''", text)  # curly quotes in LaTeX
    out = []
    for k, t, u in runs(text):
        e = tex_escape(t)
        out.append({"b": f"\\textbf{{{e}}}", "i": f"\\textit{{{e}}}", "t": e}.get(k) or f"\\href{{{u}}}{{{e}}}")
    return "".join(out)
def to_tex(lang, blocks):
    L = [r"\documentclass[10pt,a4paper]{article}",
         r"\usepackage[utf8]{inputenc}", r"\usepackage[T1]{fontenc}",
         r"\usepackage[spanish,english]{babel}" if lang == "en" else r"\usepackage[english,spanish]{babel}",
         r"\usepackage{plex-serif}\usepackage[sfdefault]{plex-sans}",
         r"\usepackage[margin=1.4cm]{geometry}", r"\usepackage{xcolor}\definecolor{navy}{HTML}{003A70}",
         r"\usepackage[colorlinks=true,urlcolor=navy]{hyperref}", r"\usepackage{titlesec}\usepackage{enumitem}",
         r"\titleformat{\section}{\serif\large\bfseries\color{navy}}{}{0pt}{}[\vspace{-0.6em}\color{navy}\rule{\linewidth}{0.8pt}]",
         r"\titlespacing*{\section}{0pt}{8pt}{4pt}",
         r"\setlist{nosep,leftmargin=1.2em}\setlength{\parindent}{0pt}\pagestyle{empty}",
         r"\newcommand{\serif}{\fontfamily{IBMPlexSerif-TLF}\selectfont}",
         r"\begin{document}",
         r"{\serif\Huge\bfseries\color{navy} Hideki Harada Oyakawa}\\[2pt]",
         r"{\small\color{gray} " + tex_escape(HEAD[lang]) + r"}\\",
         r"{\small " + r" $\cdot$ ".join(f"\\href{{{u}}}{{{tex_escape(t)}}}" for t, u in CONTACT) + r"}"]
    open_lists = []
    def close_to(level):
        while len(open_lists) > level:
            L.append(r"\end{itemize}"); open_lists.pop()
    for kind, lvl, text in blocks:
        if kind == "li":
            close_to(lvl + 1)
            while len(open_lists) < lvl + 1:
                L.append(r"\begin{itemize}"); open_lists.append(1)
            L.append(r"\item " + tex_inline(text))
        else:
            close_to(0)
            L.append(f"\\section*{{{tex_escape(text)}}}" if kind == "h" else r"\smallskip" + "\n" + tex_inline(text) + r"\par")
    close_to(0)
    L.append(r"\end{document}")
    return "\n".join(L) + "\n"

# ---------- Word ----------
def add_link(par, text, url):
    rel = par.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    h = OxmlElement("w:hyperlink"); h.set(qn("r:id"), rel)
    r = OxmlElement("w:r"); rp = OxmlElement("w:rPr")
    c = OxmlElement("w:color"); c.set(qn("w:val"), "003A70"); rp.append(c)
    u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rp.append(u)
    r.append(rp); t = OxmlElement("w:t"); t.text = text; t.set(qn("xml:space"), "preserve"); r.append(t)
    h.append(r); par._p.append(h)
def fill(par, text):
    for k, t, u in runs(text):
        if k == "a": add_link(par, t, u); continue
        run = par.add_run(t); run.bold = k == "b"; run.italic = k == "i"
def bottom_border(par):
    pPr = par._p.get_or_add_pPr(); b = OxmlElement("w:pBdr"); bt = OxmlElement("w:bottom")
    for k, v in {"val": "single", "sz": "8", "space": "1", "color": "003A70"}.items(): bt.set(qn(f"w:{k}"), v)
    b.append(bt); pPr.append(b)
def to_docx(lang, blocks, out):
    d = Document()
    for s in d.sections: s.top_margin = s.bottom_margin = Cm(1.3); s.left_margin = s.right_margin = Cm(1.6)
    st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(9.5)
    st.paragraph_format.space_after = Pt(1); st.paragraph_format.space_before = Pt(0)
    p = d.add_paragraph(); r = p.add_run("Hideki Harada Oyakawa"); r.bold = True; r.font.size = Pt(18); r.font.color.rgb = NAVY; r.font.name = "Georgia"
    p = d.add_paragraph(); r = p.add_run(HEAD[lang]); r.font.color.rgb = RGBColor(0x52, 0x60, 0x6D)
    p = d.add_paragraph()
    for i, (t, u) in enumerate(CONTACT):
        if i: p.add_run(" · ")
        add_link(p, t, u)
    for kind, lvl, text in blocks:
        if kind == "h":
            p = d.add_paragraph(); p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(3)
            r = p.add_run(text); r.bold = True; r.font.size = Pt(11.5); r.font.color.rgb = NAVY; r.font.name = "Georgia"
            bottom_border(p)
        elif kind == "li":
            p = d.add_paragraph(style="List Bullet 2" if lvl else "List Bullet"); fill(p, text)
        else:
            p = d.add_paragraph(); p.paragraph_format.space_before = Pt(4); fill(p, text)
    d.core_properties.author = "Hideki Harada Oyakawa"; d.core_properties.title = "CV – Hideki Harada Oyakawa"
    d.save(out)

for lang, src in [("en", "_pages/cv.md"), ("es", "_pages/es/cv.md")]:
    b = parse(src); base = ROOT / "files" / f"CV_Hideki_Harada_{lang.upper()}"
    base.with_suffix(".tex").write_text(to_tex(lang, b)); to_docx(lang, b, base.with_suffix(".docx"))
    print(base.with_suffix(".tex"), base.with_suffix(".docx"))
