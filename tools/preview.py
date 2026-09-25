#!/usr/bin/env python3
"""
Genera /tmp/opencode/preview/index.html: render aproximado del README
(los assets locales se inlinean como data-URI para que se vean sin
subir nada; los widgets externos siguen necesitando internet).

    python3 tools/preview.py
"""
import base64
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEST = pathlib.Path("/tmp/opencode/preview/index.html")

SHELL = '''<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"/>
<title>preview · daviddans readme</title>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
<style>
  body { background:#ffffff; margin:0; }
  .markdown-body { box-sizing:border-box; min-width:200px; max-width:980px; margin:0 auto; padding:32px;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif;
    font-size:16px; line-height:1.5; color:#1f2328; }
  .markdown-body img { max-width:100%; }
  .markdown-body pre { background:#f6f8fa; border-radius:6px; padding:16px; overflow:auto; font-size:85%;
    font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace; }
  .markdown-body code { background:rgba(175,184,193,.2); border-radius:6px; padding:.2em .4em;
    font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace; font-size:85%; }
  .markdown-body pre code { background:none; padding:0; }
  .markdown-body table { border-spacing:0; border-collapse:collapse; }
  .markdown-body td, .markdown-body th { padding:6px 13px; border:1px solid #d0d7de; }
  .markdown-body tr:nth-child(2n) td { background:#f6f8fa; }
  .markdown-body details { border:1px solid #d0d7de; border-radius:6px; padding:8px 16px; }
  .markdown-body summary { cursor:pointer; }
  .barra { max-width:980px; margin:0 auto; padding:10px 32px 10px; color:#656d76; font-size:13px;
    font-family:ui-monospace,monospace; border-bottom:1px solid #d0d7de;}
</style></head>
<body>
<div class="barra">vista previa local · render aproximado de GitHub · los &lt;details&gt; se pliegan</div>
<article id="out" class="markdown-body"></article>
<script>
  const raw = document.getElementById("md").textContent;
  document.getElementById("out").innerHTML = marked.parse(raw);
</script>
<script type="text/markdown" id="md">
'''


def main():
    md = (ROOT / "README.md").read_text()

    def inline(m):
        data = base64.b64encode((ROOT / m.group(1)).read_bytes()).decode()
        return f'src="data:image/svg+xml;base64,{data}"'

    md, n = re.subn(r'src="\./(assets/[^"]+)"', inline, md)
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(SHELL + md + "\n</script>\n</body></html>\n")
    print(f"preview: {DEST} · {DEST.stat().st_size} bytes · {n} assets inlineados")


if __name__ == "__main__":
    main()
