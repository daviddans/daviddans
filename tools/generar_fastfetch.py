#!/usr/bin/env python3
"""
Genera los paneles de terminal del hero, en DOS variantes:

  assets/fastfetch.svg        estrecha (420×452) · para móvil
  assets/fastfetch-wide.svg   ancha   (780×323) · a todo el ancho, sin foto

Las dos tienen el mismo guion (fastfetch → cat ./about_me.md → uptime →
exit), los mismos colores y el mismo tecleo. En la ancha el `about_me.md`
se escribe en una **segunda columna** a la derecha, que es lo que
aprovecha el ancho que antes ocupaba la foto.

Doble capa para que nunca se vea vacío:
  · la capa ESTATICA (texto plano, sin animación) es el estado por defecto;
  · la capa ANIMADA (un <tspan> por carácter) va encima, arrancando
    oculta, y SMIL la va "enseñando" al teclear.
  En un visor con SMIL (cualquier navegador) sólo se ve la animada; en
  uno que no lo soporte se ve la estática, completa.

    python3 tools/generar_fastfetch.py
"""
import pathlib
import sys
from datetime import date

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from svg_typing import Terminal, fmt  # noqa: E402

ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"
ARCH = pathlib.Path(__file__).resolve().parent / ".cache-iconos" / "archlinux"

# ── ritmo ─────────────────────────────────────────────────────────────────
DT_PROMPT = 0.045   # prompts y comandos
DT_TEXTO = 0.020    # contenido
PAUSA = 10.0        # segundos de lectura antes de reiniciar

# ── colores ───────────────────────────────────────────────────────────────
PROMPT_USER, PROMPT_HOST, PROMPT_SIGN = "#BB9AF7", "#7AA2F7", "#9ECE6A"
CMD, KEY, DOTS, VAL = "#E6E9FF", "#7AA2F7", "#565F89", "#E6E9FF"
TXT, TXT_HEAD, TXT_UP = "#C0CAF5", "#7DCFFF", "#9ECE6A"

# ── contenido ─────────────────────────────────────────────────────────────
CUENTA = date(2020, 2, 14)   # creación de la cuenta de GitHub


def uptime(hoy=date.today()):
    años = hoy.year - CUENTA.year - ((hoy.month, hoy.day) < (CUENTA.month, CUENTA.day))
    ultimo = date(CUENTA.year + años, CUENTA.month, CUENTA.day)
    return f"up {años} years, {(hoy - ultimo).days} days"


FASTFETCH = [   # (etiqueta, valor)
    ("user", "daviddans"),
    ("host", "fic · grupo atlante"),
    ("os", "arch linux"),
    ("shell", "zsh"),
    ("editor", "vs code · lazyvim"),
    ("degree", "SE · Computer Science"),
    ("since", "05/02/2004"),
]

ABOUT = [        # la primera línea es el encabezado del fichero
    ("# sobre_mi.md", TXT_HEAD),
    ("geek de manual: llevo rompiendo ordenadores", TXT),
    ("desde que tengo memoria. jueguitos, anime,", TXT),
    ("manga y todo lo demás. creo en el software", TXT),
    ("libre como medio para cambiar la sociedad,", TXT),
    ("y que le jodan al capitalismo.", TXT),
]

# ── geometría de cada variante ────────────────────────────────────────────
# La estrecha es la de siempre: panel en columna, about debajo.
# La ancha ocupa todo el ancho del README: logo + fastfetch a la izquierda
# y about_me en columna aparte, para que la fuente pueda ser más grande.
VARIANTES = {
    "estrecha": dict(
        salida="fastfetch.svg", W=420, H=452, TAM=11,
        X=24, IX=120, AX=None,                 # AX = columna del about
        Y1=34, LOGO=(24, 52, 62),
        LY1=70, LSTEP=19, Y2=212, AY1=246, ASTEP=19,
        YU=366, YX=410,
    ),
    "ancha": dict(
        salida="fastfetch-wide.svg", W=780, H=323, TAM=14,
        X=24, IX=108, AX=394,
        Y1=34, LOGO=(24, 58, 64),
        LY1=68, LSTEP=21, Y2=68, AY1=92, ASTEP=21,
        YU=228, YX=270,
    ),
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def prompt(comando):
    return [("daviddans", PROMPT_USER), ("@arch", PROMPT_HOST),
            (":~$ ", PROMPT_SIGN), (comando, CMD)]


def guion(g):
    """Lista de líneas: (x, y, segmentos, dt, gap, pausa)."""
    p = [(g["X"], g["Y1"], prompt("fastfetch"), DT_PROMPT, 0.10, 0.15)]
    for i, (k, v) in enumerate(FASTFETCH):
        puntos = "." * max(3, 9 - len(k))
        p.append((g["IX"], g["LY1"] + i * g["LSTEP"],
                  [(f"{k} {puntos} ", KEY), (v, VAL)], DT_TEXTO, 0.10,
                  0.55 if i == len(FASTFETCH) - 1 else 0))

    def bloque_about(x, y0, step):
        out = [(x, y0, prompt("cat ./about_me.md"), DT_PROMPT, 0.10, 0.15)]
        for i, (txt, color) in enumerate(ABOUT):
            out.append((x, y0 + g["ASTEP"] * (i + 1), [(txt, color)], DT_TEXTO, 0.10,
                        0.60 if i == len(ABOUT) - 1 else 0))
        return out

    if g["AX"]:                     # ancha: about en la 2ª columna, ya arriba
        p += bloque_about(g["AX"], g["AY1"] - g["ASTEP"], g["ASTEP"])
    else:                           # estrecha: about debajo, antes del uptime
        p += bloque_about(g["X"], g["Y2"], g["ASTEP"])

    p += [(g["X"], g["YU"], prompt("uptime"), DT_PROMPT, 0.10, 0.12),
          (g["X"] + 16, g["YU"] + g["LSTEP"], [(uptime(), TXT_UP)], DT_TEXTO, 0.10, 0.50),
          (g["X"], g["YX"], prompt("exit"), DT_PROMPT, 0.10, 0.12),
          (g["X"] + 16, g["YX"] + g["LSTEP"], [("logout", "#565F89")], DT_TEXTO, 0.10, 0)]
    return p


def generar(nombre, g):
    plan = guion(g)
    W, H, TAM = g["W"], g["H"], g["TAM"]

    # ciclo = escritura + descansos + pausa final
    escritura = sum(sum(len(s) for s, _ in seg) * dt + gap + pausa
                    for _, _, seg, dt, gap, pausa in plan)
    ciclo = escritura + PAUSA

    # capa estática (sin animación) + capa animada
    estaticas, t, t_logo = [], Terminal(ciclo), None
    for i, (x, y, seg, dt, gap, pausa) in enumerate(plan):
        plano = "".join(f'<tspan fill="{c}">{esc(s)}</tspan>' for s, c in seg)
        estaticas.append(
            f'    <text x="{x}" y="{y}" font-family="ui-monospace,Menlo,Consolas,monospace" '
            f'font-size="{TAM}" font-weight="bold" xml:space="preserve">{plano}</text>')
        t.linea(seg, x, y, size=TAM, dt=dt, gap=gap, pausa=pausa)
        if t_logo is None:                    # el logo entra tras el prompt
            t_logo = t.t
    t.cerrar(PAUSA)

    # logo (fundido al entrar) — values y keyTimes deben coincidir
    ruta = ""
    if ARCH.exists():
        svg_arch = ARCH.read_text()
        if 'd="' in svg_arch:
            ruta = svg_arch.split('d="', 1)[1].split('"', 1)[0]
    lx, ly, lado = g["LOGO"]
    esc_logo = lado / 24          # el viewBox de simple-icons es 0 0 24 24
    k_ini, k_fin = t_logo / ciclo, (t_logo + 0.45) / ciclo
    logo = (f'  <g opacity="1">\n'
            f'    <g transform="translate({lx},{ly}) scale({esc_logo:.3f})">'
            f'<path d="{ruta}" fill="#7AA2F7"/></g>\n'
            f'    <text x="{lx + lado/2}" y="{ly + lado + 14}" '
            f'font-family="ui-monospace,Menlo,Consolas,monospace" font-size="9" '
            f'fill="#565F89" text-anchor="middle">arch linux</text>\n'
            f'    <animate attributeName="opacity" dur="{fmt(ciclo)}s" '
            f'repeatCount="indefinite" calcMode="linear" values="0;0;1;1" '
            f'keyTimes="0;{fmt(k_ini)};{fmt(k_fin)};1"/>\n'
            f'  </g>') if ruta else ""

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">
  <!-- panel fastfetch del hero · generado por tools/generar_fastfetch.py -->
  <desc>fastfetch v3 {nombre} · {date.today().isoformat()} · ciclo {ciclo:.0f}s · guion: fastfetch, cat about_me, uptime, exit</desc>
  <defs>
    <linearGradient id="borde" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#F38BA8"/><stop offset=".5" stop-color="#CBA6F7"/>
      <stop offset="1" stop-color="#7DCFFF"/>
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="15" fill="#1A1B26" stroke="url(#borde)" stroke-width="2"/>

  <!-- capa estática: texto plano, la animación la deja oculta (values="0",
       un solo valor: no puede quedar mal formada y verse por encima) -->
  <g>
{chr(10).join(estaticas)}
    <animate attributeName="opacity" dur="{fmt(ciclo)}s" repeatCount="indefinite" values="0"/>
  </g>

  <!-- logo de Arch -->
{logo}

  <!-- capa animada: tecleo carácter a carácter -->
{t.svg_lineas()}

  <!-- cursor -->
{t.cursor_svg()}
</svg>
'''
    (ASSETS / g["salida"]).write_text(svg)
    print(f"{g['salida']} ({len(svg)/1024:.0f} KB · {W}×{H}px)")
    print(f"  ciclo {ciclo:.1f}s = {escritura:.1f}s escribiendo + {PAUSA:.0f}s de pausa")
    print(f"  {len(plan)} líneas · {sum(sum(len(s) for s, _ in seg) for _, _, seg, *_ in plan)}"
          f" caracteres animados · uptime: {uptime()}")
    print(f'  <img src="./assets/{g["salida"]}" width="{W}" height="{H}" alt="…"/>')


def main():
    for nombre, g in VARIANTES.items():
        generar(nombre, g)
        print()


if __name__ == "__main__":
    main()
