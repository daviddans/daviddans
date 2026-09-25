#!/usr/bin/env python3
"""
Render local del hero (y la banda de tags) tal y como lo verá GitHub,
sin depender de marked.js: extrae el HTML crudo del README y lo sirve
con CSS estilo GitHub. Solo para revisar maquetación.

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


hero = trozo('<!-- ═══════════════ $ fastfetch', '<p align="center"><img src="./assets/divider-grid.svg"')
banda = ""
cabecera = trozo('<img src="./assets/header.svg"', '<!-- ═══════════════ $ fastfetch')

CSS = """
  body { background:#0d1117; color:#c9d1d9; margin:0; padding:24px;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
  .wrap { max-width:1012px; margin:0 auto; }
  table { border-spacing:0; border-collapse:collapse; }
  td { padding:0; }
  img { max-width:100%; }
  code { background:rgba(110,118,129,.4); border-radius:6px; padding:.2em .4em;
    font-family:ui-monospace,Menlo,monospace; font-size:85%; }
  i { color:#8b949e; }
"""

HTML = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"/>
<title>test hero</title><style>{CSS}</style></head>
<body><div class="wrap">
{cabecera}
{hero}
{banda}
</div></body></html>
"""
(RAIZ / "tools" / "test-hero.html").write_text(HTML)
print("tools/test-hero.html generado")
