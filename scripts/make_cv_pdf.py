"""Builds files/CV_Hideki_Harada_EN.pdf and _ES.pdf from _pages/cv.md and _pages/es/cv.md.
Run: uv run --with markdown python scripts/make_cv_pdf.py"""
import re, subprocess, pathlib, markdown
ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://haradaoyakawahideki.github.io"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CSS = """
@page { size: A4; margin: 13mm 15mm 12mm; }
body { font-family: "IBM Plex Sans", Helvetica, Arial, sans-serif; font-size: 9pt; color:#1f2933; line-height:1.3; }
h1 { font-family: "IBM Plex Serif", Georgia, serif; color:#003A70; font-size:18pt; margin:0; }
.sub { color:#52606d; margin:2px 0 10px; font-size:9pt; }
.sub a { color:#003A70; text-decoration:none; }
h2 { font-family: "IBM Plex Serif", Georgia, serif; color:#003A70; font-size:11.5pt; border-bottom:1.5px solid #003A70; padding-bottom:2px; margin:10px 0 5px; }
p { margin:6px 0 2px; } ul { margin:2px 0 4px; padding-left:16px; } li { margin:1px 0; }
a { color:#003A70; } strong { color:#102a43; }
"""
HEAD = {
 "en": ("Political scientist · Education and public policy · Lima, Peru", "Updated"),
 "es": ("Politólogo · Educación y políticas públicas · Lima, Perú", "Actualizado"),
}
for lang, src in [("en", "_pages/cv.md"), ("es", "_pages/es/cv.md")]:
    md = (ROOT / src).read_text()
    md = re.sub(r"^---.*?---\s*", "", md, flags=re.S)
    md = re.sub(r"\{%.*?%\}", "", md)
    md = re.sub(r"(?m)^<(a|small)[^\n]*\n", "", md)  # drop download buttons/links
    md = re.sub(r"(?m)^  - ", "    - ", md)                 # nested bullets need 4 spaces
    md = re.sub(r"(?m)^([^\s-][^\n]*)\n(- )", r"\1\n\n\2", md)  # blank line before a list
    body = markdown.markdown(md)
    body = re.sub(r'href="/', f'href="{SITE}/', body)
    tag, _ = HEAD[lang]
    html = f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Serif:wght@600&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<h1>Hideki Harada Oyakawa</h1>
<p class="sub">{tag}<br><a href="mailto:harada.oyakawa.hideki@gmail.com">harada.oyakawa.hideki@gmail.com</a> · <a href="{SITE}">haradaoyakawahideki.github.io</a> · <a href="https://www.linkedin.com/in/hideki-harada">linkedin.com/in/hideki-harada</a> · <a href="https://github.com/haradaoyakawahideki">github.com/haradaoyakawahideki</a></p>
{body}</body></html>"""
    tmp = ROOT / f".cv_{lang}.html"
    tmp.write_text(html)
    out = ROOT / "files" / f"CV_Hideki_Harada_{lang.upper()}.pdf"
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=8000", f"--print-to-pdf={out}", tmp.as_uri()], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    tmp.unlink()
    print(out)
