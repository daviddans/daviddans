#!/usr/bin/env python3
"""
Genera assets/fastfetch.svg — el panel de terminal del hero:
  prompt + logo de Arch + key:value + uptime + cat ./about_me.md
  con tecleo animado y PAUSA FINAL para leerlo todo.

Doble capa para que nunca se vea vacío:
  · la capa STATICA (texto plano, sin animación) es el estado por defecto;
  · la capa ANIMADA (un <tspan> por carácter) va encima, arrancando
    oculta, y SMIL la va "enseñando" al teclear.
  En un visor con SMIL (cualquier navegador) sólo se ve la animada; en
  uno que no lo soporte se ve la estática, completa.

Para cambiar textos, colores o tiempos: edita abajo y ejecuta
    python3 tools/generar_fastfetch.py
"""
import pathlib
import sys
from datetime import date

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from svg_typing import Terminal, fmt  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "fastfetch.svg"
ARCH = pathlib.Path(__file__).resolve().parent / ".cache-iconos" / "archlinux"

# ── ritmo ─────────────────────────────────────────────────────────────────
DT_PROMPT = 0.045   # prompts y comandos
DT_TEXTO = 0.020    # contenido
PAUSA = 10.0        # segundos de lectura antes de reiniciar
GAP = 0.10
GAP_UP = 0.16

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

# ── geometría ─────────────────────────────────────────────────────────────
# Ojo: el panel se dibuja en la columna izquierda del hero, así que lo que
# se ve es ~(TAM / W) × ancho_de_la_columna.
W, H = 420, 452
X, IX = 24, 120
TAM = 11                 # tamaño de fuente del panel
Y1 = 34                  # prompt fastfetch
LOGO = (24, 52, 62)      # x, y, lado
LY1, LSTEP = 70, 19      # key:value
Y2 = 212                 # cat ./about_me.md
AY1, ASTEP = 246, 19
YU = 366                 # uptime
YX = 410                 # exit


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    # 1 · guion: (kind, x, y, segmentos, dt, gap, pausa) en orden de escritura
    #     (= orden de arriba abajo, que es como se lee)
    plan = [("cmd", X, Y1, [("daviddans", PROMPT_USER), ("@arch", PROMPT_HOST),
                            (":~$ ", PROMPT_SIGN), ("fastfetch", CMD)], DT_PROMPT, 0.10, 0.15)]
    for i, (k, v) in enumerate(FASTFETCH):
        puntos = "." * max(3, 9 - len(k))
        ultimo = i == len(FASTFETCH) - 1
        plan.append(("info", IX, LY1 + i * LSTEP,
                     [(f"{k} {puntos} ", KEY), (v, VAL)], DT_TEXTO, 0.10,
                     0.55 if ultimo else 0))          # descanso tras el bloque
    plan.append(("cmd", X, Y2, [("daviddans", PROMPT_USER), ("@arch", PROMPT_HOST),
                                (":~$ ", PROMPT_SIGN), ("cat ./about_me.md", CMD)], DT_PROMPT, 0.10, 0.15))
    for i, (txt, color) in enumerate(ABOUT):
        ultimo = i == len(ABOUT) - 1
        plan.append(("out", X, AY1 + i * ASTEP, [(txt, color)], DT_TEXTO, 0.10,
                     0.60 if ultimo else 0))
    plan.append(("cmd", X, YU, [("daviddans", PROMPT_USER), ("@arch", PROMPT_HOST),
                                (":~$ ", PROMPT_SIGN), ("uptime", CMD)], DT_PROMPT, 0.10, 0.12))
    plan.append(("out", X + 16, YU + LSTEP, [(uptime(), TXT_UP)], DT_TEXTO, 0.10, 0.50))
    plan.append(("cmd", X, YX, [("daviddans", PROMPT_USER), ("@arch", PROMPT_HOST),
                                (":~$ ", PROMPT_SIGN), ("exit", CMD)], DT_PROMPT, 0.10, 0.12))
    plan.append(("out", X + 16, YX + LSTEP, [("logout", "#565F89")], DT_TEXTO, 0.10, 0))

    # 2 · ciclo = escritura + descansos + pausa final
    escritura = sum(sum(len(s) for s, _ in seg) * dt + gap + pausa
                    for _, _, _, seg, dt, gap, pausa in plan)
    ciclo = escritura + PAUSA

    # 3 · capa estática (sin animación) + capa animada
    estaticas, t = [], Terminal(ciclo)
    t_logo = None
    for kind, x, y, seg, dt, gap, pausa in plan:
        plano = "".join(f'<tspan fill="{c}">{esc(s)}</tspan>' for s, c in seg)
        estaticas.append(
            f'    <text x="{x}" y="{y}" font-family="ui-monospace,Menlo,Consolas,monospace" '
            f'font-size="{TAM}" font-weight="bold" xml:space="preserve">{plano}</text>')
        t.linea(seg, x, y, size=TAM, dt=dt, gap=gap, pausa=pausa)
        if t_logo is None:                    # el logo entra tras el prompt
            t_logo = t.t
    t.cerrar(PAUSA)

    # 4 · logo (fundido al entrar) — values y keyTimes deben coincidir
    ruta = ""
    if ARCH.exists():
        svg_arch = ARCH.read_text()
        if 'd="' in svg_arch:
            ruta = svg_arch.split('d="', 1)[1].split('"', 1)[0]
    lx, ly, lado = LOGO
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
  <desc>fastfetch v2 · {date.today().isoformat()} · ciclo {ciclo:.0f}s · guion: fastfetch, cat about_me, uptime, exit</desc>
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
    OUT.write_text(svg)
    print(f"fastfetch.svg ({len(svg)/1024:.0f} KB)")
    print(f"  ciclo {ciclo:.1f}s = {escritura:.1f}s escribiendo + {PAUSA:.0f}s de pausa")
    print(f"  {len(plan)} líneas · {sum(sum(len(s) for s, _ in seg) for _, _, _, seg, *_ in plan)} caracteres animados · uptime: {uptime()}")


if __name__ == "__main__":
    main()
