#!/usr/bin/env python3
"""
Genera assets/header.svg — cabecera original del perfil:
  · prompt de terminal
  · escena synthwave (sol con rayas, rejilla en perspectiva, estrellas)
  · typing animado tipo máquina de escribir en SVG puro (SMIL), con el
    motor compartido tools/svg_typing.py: el cursor va sólido mientras
    escribe, se queda un espacio en blanco al terminar la frase y
    parpadea durante la pausa.

Para cambiar los taglines, colores o tiempos: edita PROMPT / LINEAS /
DT / PAUSA y vuelve a ejecutar:

    python3 tools/generar_header.py

Sin dependencias: solo Python 3.
"""
import pathlib
import sys
from datetime import date

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from svg_typing import Terminal, fmt  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "header.svg"

# ── prompt de la cabecera: (texto, color) ────────────────────────────────
PROMPT = [
    ("daviddans", "#BB9AF7"),
    ("@",         "#C0CAF5"),
    ("arch",      "#7AA2F7"),
    (":~$",       "#9ECE6A"),
]
PROMPT_FONT = 50
PROMPT_X, PROMPT_Y = 52, 102
PROMPT_CUR = (18, 40, 68)      # w, h, y del cursor junto al prompt

# ── frases del typing: (texto, color) ────────────────────────────────────
LINEAS = [
    ("~ I use arch btw ~",                  "#7AA2F7"),
    ("average free & open source enjoyer.", "#9ECE6A"),
    ("Software engineer | Computer Science.", "#F9E2AF"),
    ("Gamedev wannabe.",                    "#F5BDE6"),
    ("Code, Hack, Coffee. Repeat...",       "#7DCFFF"),
]
TYPE_FONT = 22
TYPE_X, TYPE_Y = 52, 164
CUR_W, CUR_H = 12, 23

# ── tiempos del ciclo (segundos) ──────────────────────────────────────────
DT = 0.045      # teclear un carácter
PAUSA = 5.0     # descanso con la frase terminada (aquí parpadea el cursor)
DT_DEL = 0.025  # borrar la frase antes de la siguiente
GAP = 0.15      # margen entre el borrado y la frase siguiente

hexc = lambda c: c if c.startswith("#") else f"#{c}"
esc = lambda s: "".join({"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(c, c) for c in s)


def bloque_escena():
    """Sol de atardecer con rayas, rejilla en perspectiva y estrellas."""
    return '''  <defs>
    <linearGradient id="sunset" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#F38BA8"/>
      <stop offset=".55" stop-color="#FAB387"/>
      <stop offset="1" stop-color="#F9E2AF"/>
    </linearGradient>
    <linearGradient id="horizon" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#F38BA8"/>
      <stop offset=".5" stop-color="#CBA6F7"/>
      <stop offset="1" stop-color="#7DCFFF"/>
    </linearGradient>
    <mask id="rayas">
      <rect x="700" y="0" width="220" height="131" fill="#fff"/>
      <rect x="700" y="86" width="220" height="6" fill="#000"/>
      <rect x="700" y="100" width="220" height="8" fill="#000"/>
      <rect x="700" y="116" width="220" height="10" fill="#000"/>
    </mask>
  </defs>

  <rect width="1000" height="200" rx="28" fill="#1A1B26"/>

  <!-- escena: sol sobre el horizonte + rejilla en perspectiva -->
  <circle cx="810" cy="130" r="72" fill="url(#sunset)" mask="url(#rayas)">
    <animate attributeName="opacity" values="1;.82;1" dur="3.2s" repeatCount="indefinite"/>
  </circle>
  <rect x="690" y="130" width="240" height="4" fill="url(#horizon)" opacity=".85"/>
  <g stroke-linecap="round">
    <path d="M810 131 L724 200" stroke="#7AA2F7" opacity=".55"/>
    <path d="M810 131 L768 200" stroke="#7DCFFF" opacity=".55"/>
    <path d="M810 131 L852 200" stroke="#CBA6F7" opacity=".55"/>
    <path d="M810 131 L896 200" stroke="#7AA2F7" opacity=".55"/>
    <path d="M810 131 L680 200" stroke="#CBA6F7" opacity=".3"/>
    <path d="M810 131 L940 200" stroke="#7DCFFF" opacity=".3"/>
    <g>
      <path d="M793 140 H827" stroke="#7AA2F7"/>
      <path d="M769 153 H851" stroke="#7DCFFF"/>
      <path d="M738 169 H882" stroke="#CBA6F7"/>
      <path d="M705 187 H915" stroke="#7AA2F7"/>
      <animateTransform attributeName="transform" type="translate" values="0 0;0 16" dur="1.6s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="1;.1" dur="1.6s" repeatCount="indefinite"/>
    </g>
  </g>

  <!-- estrellitas -->
  <g>
    <rect x="690" y="34" width="8" height="8" fill="#7DCFFF"><animate attributeName="opacity" values="1;.15;1" dur="1.4s" repeatCount="indefinite"/></rect>
    <rect x="940" y="52" width="8" height="8" fill="#CBA6F7"><animate attributeName="opacity" values="1;.15;1" dur="1.4s" begin=".4s" repeatCount="indefinite"/></rect>
    <rect x="730" y="12" width="6" height="6" fill="#F5BDE6"><animate attributeName="opacity" values="1;.2;1" dur="1.8s" begin=".8s" repeatCount="indefinite"/></rect>
    <rect x="905" y="18" width="6" height="6" fill="#F9E2AF"><animate attributeName="opacity" values="1;.2;1" dur="1.8s" begin="1.1s" repeatCount="indefinite"/></rect>
    <rect x="640" y="60" width="6" height="6" fill="#7AA2F7"><animate attributeName="opacity" values="1;.25;1" dur="2.2s" begin=".2s" repeatCount="indefinite"/></rect>
  </g>
'''


def main():
    ciclo = sum(len(t) * DT + PAUSA + len(t) * DT_DEL + GAP for t, _ in LINEAS)

    # el cursor arranca detrás del prompt y luego salta a la primera frase
    prompt_ancho = sum(len(s) for s, _ in PROMPT) * PROMPT_FONT * 0.6
    t = Terminal(ciclo, cursor_inicio=(PROMPT_X + prompt_ancho + 8, PROMPT_CUR[2]))
    for texto, color in LINEAS:
        t.linea([(texto, hexc(color))], TYPE_X, TYPE_Y, size=TYPE_FONT,
                dt=DT, gap=GAP, pausa=PAUSA, borrar=True, dt_del=DT_DEL)
    t.cerrar(0)

    prompt_spans = "".join(f'<tspan fill="{c}">{esc(s)}</tspan>' for s, c in PROMPT)
    largo = max(len(s) for s, _ in LINEAS)
    ancho_max = TYPE_X + largo * TYPE_FONT * 0.6 + CUR_W
    print(f"  frases: {len(LINEAS)} · la más larga acaba en x={ancho_max:.0f} "
          f"(la escena empieza en 640)")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="200" viewBox="0 0 1000 200" fill="none">
  <!-- cabecera original: prompt + escena synthwave + typing animado (SMIL) -->
  <!-- generado por tools/generar_header.py · editar frases ahí -->
  <desc>header v2 · {date.today().isoformat()} · ciclo {ciclo:.0f}s · {PAUSA:.0f}s de pausa por frase</desc>
{bloque_escena()}
  <!-- prompt -->
  <text font-family="ui-monospace,Menlo,Consolas,monospace" font-size="{PROMPT_FONT}" font-weight="bold" x="{PROMPT_X}" y="{PROMPT_Y}">{prompt_spans}</text>

  <!-- typing: una frase cada vez, con su descanso -->
{t.svg_lineas()}

  <!-- cursor: sólido al escribir, parpadea en las pausas -->
{t.cursor_svg(w=CUR_W, h=CUR_H, color="#7AA2F7", parpadeo=1.1)}
</svg>
'''
    OUT.write_text(svg)
    print(f"header.svg generado ({len(svg)/1024:.0f} KB)")
    print(f"  ciclo {ciclo:.1f}s = {len(LINEAS)} frases · {PAUSA:.0f}s de pausa en cada una")


if __name__ == "__main__":
    main()
