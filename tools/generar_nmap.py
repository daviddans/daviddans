#!/usr/bin/env python3
"""
Genera assets/nmap.svg — la sección de contacto del final del perfil.

No es un SSH: es un `nmap -sV` a daviddans, donde cada "puerto abierto"
es una de tus cosas (los puertos reales de cada servicio, para que el
chiste se entienda: 8006 es Proxmox, 9100 una impresora, 51820 WireGuard…).

Se escribe una sola vez (loop=False) y el cursor se queda parpadeando
para siempre al final, en el prompt: es lo último del perfil y si te
quedas a medio bajar no quieres perderte la lista.

OJO: el correo, el Steam y el Instagram están también en el README (en
las badges, que sí son clicables; un SVG no lo es). Si los cambias,
cámbialos en los dos sitios y vuelve a ejecutar este script.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from svg_typing import Terminal, esc, fmt  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "nmap.svg"
MONO = "ui-monospace,Menlo,Consolas,monospace"

# ── ritmo ─────────────────────────────────────────────────────────────────
DT = 0.014        # s por carácter (sale rápido: son muchas líneas)
PAUSA = 0.16      # descanso entre líneas
TAM = 15
LSTEP = 23
MARGEN = 24

# ── paleta ───────────────────────────────────────────────────────────────
TXT, SUB, OK, WARN = "#C0CAF5", "#7A7FA6", "#9ECE6A", "#F9E2AF"
SRV, DEST, DIM = "#7DCFFF", "#E6E9FF", "#565F89"
USER, HOST, SIGN = "#BB9AF7", "#7AA2F7", "#9ECE6A"

# ── el escaneo ───────────────────────────────────────────────────────────
# (puerto, servicio, versión, destino)
PUERTOS = [
    ("22/tcp",     "ssh",       "OpenSSH 9.6p1",  "github.com/daviddans"),
    ("80/tcp",     "http",      "nginx 1.26.0",   "daviddans.dev"),
    ("443/tcp",    "ssl/http",  "Instagram",      "@{{TU_INSTAGRAM}}"),
    ("993/tcp",    "imaps",     "dovecot 2.3.19", "dans.villares@gmail.com"),
    ("1883/tcp",   "mqtt",      "mosquitto 2.0.18", "home assistant"),
    ("2376/tcp",   "docker",    "27.3.1",         "homelab · dockerd"),
    ("3000/tcp",   "http",      "Grafana 11.3.0", "dashboards"),
    ("3478/udp",   "stun",      "steam",          "{{TU_STEAM}}"),
    ("8006/tcp",   "proxmox",   "PVE 8.2.4",       "proxmox.home"),
    ("8443/tcp",   "ssl/http",  "LinkedIn",       "in/daviddans"),
    ("9100/tcp",   "printer",   "OctoPrint 1.9.3", "mi impresora 3D"),
    ("27015/tcp",  "steam",     "Steam 3",        "{{TU_STEAM}}"),
    ("51820/udp",  "wireguard", "wg0",            "tailnet"),
]

CABECERA = ("PORT", "STATE", "SERVICE", "VERSIÓN", "DESTINO")
COLORES = (TXT, OK, SRV, TXT, DEST)     # color de cada columna


def celdas(p):
    """(puerto, servicio, versión, destino) → las 5 columnas de la fila."""
    return [p[0], "open", p[1], p[2], p[3]]


def columnas():
    """Ancho de cada columna (la del contenido más largo + 2 de separación)."""
    return [max([len(cab)] + [len(c[i]) for c in map(celdas, PUERTOS)]) + 2
            for i, cab in enumerate(CABECERA)]


def ancho():
    """Ancho total en caracteres (la tabla manda)."""
    return sum(columnas())


def fila(celdas, colores):
    """Rellena con espacios para que las columnas cuadren (es monoespaciado)."""
    an = columnas()
    return [(c.ljust(an[i]), colores[i]) for i, c in enumerate(celdas)]


def lineas():
    """Cada línea: [(texto, color)…] (o [] para una línea en blanco)."""
    out = [
        [("Starting Nmap 7.95 ( https://nmap.org )", SUB)],
        [("Nmap scan report for ", SUB), ("daviddans", TXT)],
        [("Host is up ", OK), ("(0.041s latency).", SUB)],
        [("Not shown: ", SUB), ("977 closed ports", DIM)],
        [],
        fila(list(CABECERA), (SUB,) * len(CABECERA)),
    ]
    for p in PUERTOS:
        out.append(fila(celdas(p), COLORES))
    out += [
        [],
        [("Nmap done: 1 IP address (1 host up) scanned in 0.84 seconds", SUB)],
        [],
        [("daviddans", USER), ("@arch", HOST), (":~$ ", SIGN)],
    ]
    return out


def main():
    cw = TAM * 0.6
    W = int(ancho() * cw) + MARGEN * 2
    guion = lineas()
    H = MARGEN + TAM + LSTEP * len(guion) + 12

    total = sum(sum(len(txt) for txt, _ in l) for l in guion) * DT
    ciclo = total + PAUSA * len(guion) + 5.0
    t = Terminal(ciclo, loop=False)

    estaticas, y = [], MARGEN + TAM
    for lin in guion:
        if lin:
            plano = "".join(f'<tspan fill="{c}">{esc(txt)}</tspan>'
                            for txt, c in lin)
            estaticas.append(
                f'    <text x="{MARGEN}" y="{y}" font-family="{MONO}" '
                f'font-size="{TAM}" font-weight="bold" xml:space="preserve">'
                f'{plano}</text>')
            t.linea(lin, MARGEN, y, size=TAM, dt=DT, gap=PAUSA)
        else:                       # línea en blanco: sólo mueve el cursor
            t.linea([(" ", DIM)], MARGEN, y, size=TAM, dt=DT, gap=PAUSA)
        y += LSTEP
    t.cerrar()

    # cursor: se congela al terminar y luego parpadea para siempre
    _, cx, cy = t.movs[-1]
    alto = round(TAM * 1.08)
    cursor = f'''  <rect x="{cx:.1f}" y="{cy:.1f}" width="8" height="{alto}" fill="#7AA2F7" opacity="0">
    <animate attributeName="opacity" dur="{fmt(ciclo)}s" repeatCount="1" fill="freeze"
             calcMode="linear" values="0;0;1;1" keyTimes="0;{fmt((ciclo - 0.05) / ciclo)};1"/>
  </rect>
  <rect x="{cx:.1f}" y="{cy:.1f}" width="8" height="{alto}" fill="#7AA2F7" opacity="0">
    <animate attributeName="opacity" values="1;0" keyTimes="0;.5" calcMode="discrete"
             dur="1.1s" begin="{fmt(ciclo)}s" repeatCount="indefinite"/>
  </rect>'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">
  <!-- nmap de contacto · generado por tools/generar_nmap.py -->
  <desc>nmap v1 · escribe una vez y el cursor parpadea · {len(PUERTOS)} puertos abiertos: github, mail, linkedin, steam, instagram, homelab, proxmox y la impresora 3D</desc>
  <defs>
    <linearGradient id="borde" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#9ECE6A"/><stop offset=".5" stop-color="#F9E2AF"/>
      <stop offset="1" stop-color="#F38BA8"/>
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="#1A1B26" stroke="url(#borde)" stroke-width="2"/>

  <!-- barra de título -->
  <rect x="16" y="15" width="9" height="9" rx="2" fill="#F38BA8"/>
  <rect x="30" y="15" width="9" height="9" rx="2" fill="#F9E2AF"/>
  <rect x="44" y="15" width="9" height="9" rx="2" fill="#9ECE6A"/>
  <text x="{W/2:.0f}" y="23" text-anchor="middle" font-family="{MONO}" font-size="10" fill="#565F89">nmap -sV -T4 daviddans</text>
  <line x1="1" y1="34" x2="{W-1}" y2="34" stroke="#2A2F45" stroke-width="1"/>

  <!-- capa estática (visible si el visor no soporta SMIL) -->
  <g>
{chr(10).join(estaticas)}
    <animate attributeName="opacity" dur="{fmt(ciclo)}s" repeatCount="indefinite" values="0"/>
  </g>

  <!-- capa animada: tecleo -->
{t.svg_lineas()}

  <!-- cursor -->
{cursor}
</svg>
'''
    OUT.write_text(svg)
    print(f"nmap.svg ({len(svg)/1024:.1f} KB · {W}×{H}px)")
    print(f"  {len(PUERTOS)} puertos · {len(guion)} líneas · escribe {total:.1f}s, "
          f"ciclo {ciclo:.1f}s y luego el cursor parpadea")
    print(f'  <img src="./assets/nmap.svg" width="{W}" height="{H}" alt="…"/>')


if __name__ == "__main__":
    main()
