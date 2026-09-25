#!/usr/bin/env python3
"""
Genera las etiquetas (badges) del hero y las inserta en README.md
entre los marcadores <!-- BEGIN TAGS:… --> / <!-- END TAGS:… -->.

Ventajas frente a escribirlas a mano:
  · el emoji va URL-encoded bien a la primera (los %F0%9F… se escriben fatal a mano);
  · las líneas se reparten por ancho estimado, así nada se desborda;
  · para cambiar un tag editas la lista y ejecutas esto.

    python3 tools/generar_tags.py
"""
import pathlib
import re
import urllib.parse

RAIZ = pathlib.Path(__file__).resolve().parent.parent
README = RAIZ / "README.md"

# ── identidad (columna izquierda, junto a la foto) ────────────────────────
IDENTIDAD = [
    ("🎓", "SE · Computer Science", "F9E2AF"),
    ("🏛️", "FIC · UDC", "F5BDE6"),
    ("💼", "grupo atlante", "7AA2F7"),
    ("🐧", "arch, btw", "7DCFFF"),
    ("💚", "open source", "9ECE6A"),
]

# ── banda inferior: hobbies tech / hobbies / soft skills ─────────────────
TECH = [
    ("🏠", "homelab & selfhosting", "CBA6F7"),
    ("🔐", "seguridad & CTF", "F38BA8"),
    ("⚡", "electrónica & soldadura", "9ECE6A"),
    ("🖨️", "impresión 3D", "7DCFFF"),
    ("🎮", "gamedev", "F5BDE6"),
    ("🧠", "machine learning", "7DCFFF"),
    ("📡", "redes & servidores", "7AA2F7"),
    ("🤖", "automatizarlo todo", "FAB387"),
    ("🏆", "hackudc survivor", "CBA6F7"),
]

OFFLINE = [
    ("🎮", "videojuegos", "F5BDE6"),
    ("📚", "anime & manga", "CBA6F7"),
    ("🎬", "cine", "7AA2F7"),
    ("🎵", "música", "7DCFFF"),
    ("🎨", "diseño & dibujo", "F9E2AF"),
    ("🏋️", "gym", "9ECE6A"),
    ("🚗", "coches & motor", "F38BA8"),
    ("🐾", "animales", "FAB387"),
    ("☕", "café", "F5BDE6"),
]

SOFT = [
    ("🤝", "trabajo en equipo", "7AA2F7"),
    ("🧩", "resolución de problemas", "9ECE6A"),
    ("🚀", "aprender rápido", "F5BDE6"),
    ("📝", "documentación", "FAB387"),
    ("🗣️", "comunicación", "7DCFFF"),
    ("🔍", "curiosidad", "F9E2AF"),
]


ESCALA = 1.2      # las badges se agrandan con height="24" (shields usa 20)
ALTO = 24
COL = 255          # ancho máximo de una fila de tags en las sub-columnas


def ancho(it):
    """Ancho real aproximado de una badge flat-square, medido en shields:
    los glifos ocupan 5.12 px por carácter (+ el emoji) y hay ~31 px fijos."""
    emoji, texto = it[0], it[1]
    largo = len(texto) + (2 if emoji else 0)
    return (5.12 * largo + 31) * ESCALA


def esc(s):
    return s.replace("&", "&amp;")


def badge(emoji, texto, color):
    msg = urllib.parse.quote(f"{emoji}-{texto}".replace(" ", "%20"), safe="%")
    return (f'<img src="https://img.shields.io/badge/{msg}-{color}?style=flat-square" '
            f'height="{ALTO}" alt="{esc(texto)}"/>')


def grupo(nombre, items, max_px, centrar=True):
    """Etiqueta + tabla interna: todas las filas alineadas a la izquierda."""
    filas, actual, usado = [], [], 0
    for it in items:
        w = ancho(it)
        if actual and usado + w > max_px:
            filas.append(actual)
            actual, usado = [], 0
        actual.append(badge(*it))
        usado += w
    if actual:
        filas.append(actual)
    align = "center" if centrar else "left"
    html = [f'      <p align="center"><code>{nombre}</code></p>',
            f'      <table border="0" align="{align}">']
    for f in filas:
        html.append("        <tr><td align=\"left\">" + " ".join(f) + "</td></tr>")
    html.append("      </table>")
    return "\n".join(html)


def bloque(inicio, fin, contenido):
    md = README.read_text()
    a = md.index(inicio) + len(inicio)
    b = md.index(fin)
    README.write_text(md[:a] + "\n" + contenido + "\n" + md[b:])


def validar(todos):
    """Comprueba que ninguna badge devuelva 'badge not found'.

    OJO: shields separa el path por guiones, así que un texto con '-'
    JUNTO a un emoji rompe la URL (404). De ahí este chequeo.
    """
    import urllib.request
    import concurrent.futures
    urls = [badge(*it) for it in todos]
    urls = [re.search(r'src="([^"]+)"', u).group(1) for u in urls]

    def chk(u):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20)
            svg = r.read().decode()
            return u, ("badge not found" in svg or r.status != 200)
        except Exception:
            return u, True

    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        rotas = [u for u, mal in ex.map(chk, urls) if mal]
    if rotas:
        print(f"  ⚠️  {len(rotas)} badge(s) rotas (revisa los guiones o el emoji):")
        for u in rotas:
            print("     ", u)
    else:
        print(f"  ✓ {len(urls)} badges comprobadas: ninguna rota")


def main():
    # · columna de la foto: dos sub-columnas con los cuatro grupos
    colA = "\n".join([
        grupo("~/identidad", IDENTIDAD, COL, centrar=True),
        grupo("~/.soft-skills", SOFT, COL, centrar=True),
    ])
    colB = "\n".join([
        grupo("~/.hobbies/tech", TECH, COL, centrar=True),
        grupo("~/.hobbies", OFFLINE, COL, centrar=True),
    ])
    hero = ('<table border="0" align="center">\n        <tr>\n'
            f'          <td valign="top" align="left">\n{colA}\n          </td>\n'
            f'          <td valign="top" align="left">\n{colB}\n          </td>\n'
            '        </tr>\n      </table>')

    bloque("<!-- BEGIN TAGS:HERO -->", "<!-- END TAGS:HERO -->", hero)
    total = sum(len(g) for g in (IDENTIDAD, TECH, OFFLINE, SOFT))
    print(f"tags generadas: {total} "
          f"(identidad {len(IDENTIDAD)} · tech {len(TECH)} · "
          f"hobbies {len(OFFLINE)} · soft {len(SOFT)})")
    validar(IDENTIDAD + TECH + OFFLINE + SOFT)


if __name__ == "__main__":
    main()
