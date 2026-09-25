#!/usr/bin/env python3
"""
Genera assets/ssh.svg — la sesión de contacto del final del perfil:

    daviddans@arch:~$ ssh guest@daviddans.dev
    guest@daviddans.dev's password: ********
    ...
    guest@daviddans:~$ █

Se escribe una sola vez (loop=False) y el cursor se queda parpadeando
para siempre: es la última cosa del perfil, y si te queda mal con la
página a medio bajar no quieres perderte el texto.

OJO: el correo y el LinkedIn también están en el README (en las badges,
que sí son clicables; un SVG no lo es). Si los cambias, cámbialos en los
dos sitios y vuelve a ejecutar este script.
"""
import datetime
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from svg_typing import Terminal, esc, fmt  # noqa: E402
# la fecha de la cuenta vive en el generador del panel: se importa para que
# el "uptime" del ssh y el del fastfetch nunca se contradigan
from generar_fastfetch import CUENTA  # noqa: E402


def antiguedad(hoy=None):
    """'6 años' a partir de la fecha de creación de la cuenta."""
    d = (hoy or datetime.date.today()) - CUENTA
    años = d.days // 365
    return f"{años} {'año' if años == 1 else 'años'}"

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "ssh.svg"
MONO = "ui-monospace,Menlo,Consolas,monospace"

# ── ritmo ─────────────────────────────────────────────────────────────────
DT = 0.030        # s por carácter
PAUSA = 0.55      # descanso entre líneas
MARGEN = 22
TAM = 12
LSTEP = 19
TITULO = "ssh guest@daviddans.dev"
X0 = MARGEN

# ── paleta ───────────────────────────────────────────────────────────────
USER, HOST, SIGN = "#BB9AF7", "#7AA2F7", "#9ECE6A"
CMD, OK, TXT, SUB = "#E6E9FF", "#9ECE6A", "#C0CAF5", "#565F89"
KEY, NUM, WARN = "#7AA2F7", "#7DCFFF", "#FAB387"

# ── contenido ────────────────────────────────────────────────────────────
# cada entrada: (sangría, clave, [(texto, color)…])  ·  "" = sin clave
GUION = [
    (0, "", [("daviddans@arch", USER), (":~$ ", SUB),
             ("ssh guest@daviddans.dev", CMD)]),
    (0, "", [("guest@daviddans.dev's password: ", SUB), ("********", WARN)]),
    (0, "", []),                                   # línea en blanco
    (0, "", [("  Welcome to ", TXT), ("daviddans v26 · LTS", KEY),
             (" (x86_64)", SUB)]),
    (0, "", []),
    (0, "", [("  uptime", SUB), (" ....... ", SUB), (antiguedad(), NUM)]),
    (0, "", [("  whoami", SUB), (" ....... ", SUB), ("daviddans", TXT)]),
    (0, "", [("  docs", SUB), (" ......... ", SUB), ("github.com/daviddans", TXT)]),
    (0, "", [("  mail", SUB), (" ......... ", SUB), ("dans.villares@gmail.com", TXT)]),
    (0, "", [("  linkedin", SUB), (" ..... ", SUB), ("in/daviddans", TXT)]),
    (0, "", []),
    (0, "", [("  session", SUB), (" ... ", SUB),
             ("abierta — escríbeme y hablamos", OK)]),
    (0, "", []),
    (0, "", [("guest@daviddans", USER), (":~$ ", SUB)]),
]


def columnas(sangria, clave, segs):
    if clave:
        segs = [(clave + ":", KEY)] + [s for s in segs if s[0]]
    return sangria + sum(len(t) for t, _ in segs), segs


def main():
    ancho_char = TAM * 0.6
    ncols = max(columnas(s, c, g)[0] for s, c, g in GUION)
    W = int(ncols * ancho_char) + MARGEN * 2
    H = MARGEN * 2 + 34 + LSTEP * len(GUION) + 10

    # ── tiempos ──────────────────────────────────────────────────────────
    total = sum(columnas(s, c, g)[0] for s, c, g in GUION) * DT
    ciclo = total + PAUSA * len(GUION) + 4.0        # 4 s de pausa final
    t = Terminal(ciclo, loop=False)

    # ── escritura ────────────────────────────────────────────────────────
    estaticas, y = [], MARGEN + 34 + TAM
    for sangria, clave, segs in GUION:
        n, segs = columnas(sangria, clave, segs)
        x = X0 + sangria * ancho_char
        if segs:
            estaticas.append(
                f'    <text x="{x:.1f}" y="{y}" font-family="{MONO}" '
                f'font-size="{TAM}" font-weight="bold" xml:space="preserve">'
                + "".join(f'<tspan fill="{c}">{esc(x_)}</tspan>' for x_, c in segs)
                + "</text>")
            t.linea(segs, x, y, size=TAM, dt=DT, gap=PAUSA)
        else:
            t.linea([(" ", SUB)], x, y, size=TAM, dt=DT, gap=PAUSA)
        y += LSTEP
    t.cerrar()

    # cursor: el del motor, congelado al final, + un parpadeo propio para
    # que siga vivo después de que la animación se congele
    _, cx, cy = t.movs[-1]
    cursor = f'''  <rect x="{cx:.1f}" y="{cy:.1f}" width="7" height="{round(TAM * 1.08)}" fill="#7AA2F7" opacity="0">
    <animate attributeName="opacity" dur="{fmt(ciclo)}s" repeatCount="1" fill="freeze"
             calcMode="linear" values="0;0;1;1" keyTimes="0;{fmt((ciclo - 0.05) / ciclo)};1"/>
  </rect>
  <rect x="{cx:.1f}" y="{cy:.1f}" width="7" height="{round(TAM * 1.08)}" fill="#7AA2F7" opacity="0">
    <animate attributeName="opacity" values="1;0" keyTimes="0;.5" calcMode="discrete"
             dur="1.1s" begin="{fmt(ciclo)}s" repeatCount="indefinite"/>
  </rect>'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">
  <!-- sesión ssh de contacto · generado por tools/generar_ssh.py -->
  <desc>ssh v1 · escribe una vez y el cursor parpadea · contacta por mail, linkedin o github</desc>
  <defs>
    <linearGradient id="borde" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#9ECE6A"/><stop offset=".5" stop-color="#7AA2F7"/>
      <stop offset="1" stop-color="#BB9AF7"/>
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="#1A1B26" stroke="url(#borde)" stroke-width="2"/>

  <!-- barra de título -->
  <rect x="16" y="15" width="9" height="9" rx="2" fill="#F38BA8"/>
  <rect x="30" y="15" width="9" height="9" rx="2" fill="#F9E2AF"/>
  <rect x="44" y="15" width="9" height="9" rx="2" fill="#9ECE6A"/>
  <text x="{W/2:.0f}" y="23" text-anchor="middle" font-family="{MONO}" font-size="10" fill="{SUB}">{TITULO}</text>
  <line x1="1" y1="34" x2="{W-1}" y2="34" stroke="#2A2F45" stroke-width="1"/>

  <!-- capa estática (visible si el visor no soporta SMIL) -->
  <g>
{chr(10).join(estaticas)}
    <animate attributeName="opacity" dur="{fmt(ciclo)}s" repeatCount="indefinite" values="0"/>
  </g>

  <!-- capa animada: tecleo -->
{t.svg_lineas()}

  <!-- cursor: se congela al terminar y luego parpadea -->
{cursor}
</svg>
'''
    OUT.write_text(svg)
    print(f"ssh.svg ({len(svg)/1024:.1f} KB · {W}×{H}px)")
    print(f"  {len(GUION)} líneas · {ncols} columnas · escribe {total:.1f}s + pausas "
          f"= {ciclo:.1f}s, y luego el cursor parpadea")
    print(f'  <img src="./assets/ssh.svg" width="{W}" height="{H}" alt="…"/>')


if __name__ == "__main__":
    main()
