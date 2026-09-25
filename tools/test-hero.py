#!/usr/bin/env python3
"""
Render local del hero tal y como lo ve GitHub HOY, sin marked.js:
extrae el HTML crudo del README y lo sirve con una copia del CSS de
GitHub (.markdown-body), que es lo que manda en la maquetación.

OJO: desde 2023 GitHub **bordea las celdas de las tablas** y pone
`display:block; width:max-content` en cada `<table>`. Eso cambia mucho
las cosas: una celda con mucho contenido estira a su hermana y deja un
rectángulo vacío debajo. Este arnés reproduce esas dos reglas a propósito,
que si no no se ve el fallo hasta que lo subes.

    python3 tools/test-hero.py
    python3 -m http.server 8766   # y abre /tools/test-hero.html
"""
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
md = (RAIZ / "README.md").read_text()


def trozo(inicio, fin):
    a = md.index(inicio)
    b = md.index(fin, a)
    # rutas absolutas: la página vive en /tools/
    return md[a:b].replace('src="./assets/', 'src="/assets/')


cabecera = trozo('<img src="./assets/header.svg"', '<!-- ═══════════════ $ fastfetch')
hero = trozo('<!-- ═══════════════ $ fastfetch',
             '<p align="center"><img src="./assets/divider-wave.svg"')

# ── CSS copiado del que GitHub aplica a .markdown-body ───────────────────
CSS = """
  body { background:#0d1117; color:#c9d1d9; margin:0; padding:24px;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
  .wrap { max-width:878px; margin:0 auto; }
  .markdown-body { font-size:16px; line-height:1.5; word-wrap:break-word; }
  .markdown-body table { display:block; width:max-content; max-width:100%;
    overflow:auto; border-spacing:0; border-collapse:collapse; }
  .markdown-body table th, .markdown-body table td {
    padding:6px 13px; border:1px solid #30363d; }
  .markdown-body table tr { border-top:1px solid #30363d; }
  .markdown-body p, .markdown-body blockquote { margin-top:0; margin-bottom:16px; }
  .markdown-body img { max-width:100%; box-sizing:content-box; background-color:#fff; }
  .markdown-body code { background:rgba(110,118,129,.4); border-radius:6px; padding:.2em .4em;
    font-family:ui-monospace,Menlo,monospace; font-size:85%; }
  .markdown-body i { color:#8b949e; }
  /* los SVG son transparentes: nada de fondo blanco */
  .markdown-body img[src$=".svg"] { background-color:transparent; }
"""

HTML = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>test hero</title><style>{CSS}</style></head>
<body><div class="wrap"><div class="markdown-body">
{cabecera}
{hero}
</div></div></body></html>
"""
(RAIZ / "tools" / "test-hero.html").write_text(HTML)
print("tools/test-hero.html generado")
