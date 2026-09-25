#!/usr/bin/env python3
"""
Genera los strips de iconos assets/stack-*.svg del tree del README.

Cada strip es una fila de tiles uniformes (256px, rx 60, gap 44) con la
misma geometría que skill-icons, compuesta de tres fuentes:
  · repo  → SVG oficial de skill-icons (tandpfun, MIT)
  · si    → logo de simple-icons vía CDN, recoloreado si es demasiado
            oscuro para el fondo (#242938)
  · draw  → tile dibujado a mano (matplotlib, pygame, gymnasium)
  · text  → tile de texto (SB3, ESP32, CSP)

Para cambiar el stack (añadir un juego, una librería…):
 1. edita STRIPS abajo
 2. ejecuta:  python3 tools/generar_strips.py
 3. copia el <img width="…"> que imprime en el README

Requiere red la primera vez (descarga los logos). Sin dependencias.
"""
import pathlib
import re
import subprocess
import time
import urllib.request

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets"
CACHE = pathlib.Path(__file__).resolve().parent / ".cache-iconos"
SKILL_REPO = "https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/"
SIMPLE_ICONS = "https://cdn.simpleicons.org/"

# ── strips atenuados: se leen "en proceso" sin escribirlo ────────────────
TENUE = {"stack-learning": 0.55}

# ── qué contiene cada strip ──────────────────────────────────────────────
# (repo = skill-icons · si = simple-icons · text = tile de texto)
STRIPS = {
    "stack-langs":      [("repo", "C"), ("repo", "CPP"), ("repo", "CS"),
                         ("repo", "Python-Dark"), ("repo", "Java-Dark"),
                         ("repo", "Bash-Dark")],
    "stack-learning":   [("repo", "JavaScript"), ("repo", "TypeScript"),
                         ("repo", "Flutter-Dark"), ("si", "erlang"),
                         ("repo", "Lua-Dark")],
    "stack-tools":      [("repo", "Git"), ("repo", "VSCode-Dark"),
                         ("repo", "VisualStudio-Dark"), ("si", "lazyvim"),
                         ("si", "alacritty"), ("text", ("ZELLIJ", "#9ECE6A", 50)),
                         ("repo", "Obsidian")],
    "stack-frameworks": [("repo", "DotNet"), ("repo", "React-Dark"),
                         ("repo", "NextJS-Dark"), ("repo", "FastAPI"),
                         ("repo", "Spring-Dark")],
    "stack-pylibs":     [("si", "numpy"), ("draw", "mpl"), ("draw", "pygame")],
    "stack-ml":         [("repo", "PyTorch-Dark"), ("si", "scikitlearn"),
                         ("si", "huggingface"), ("draw", "gym"),
                         ("text", ("SB3", "#7DCFFF", 72))],
    "stack-infra":      [("repo", "Linux-Dark"), ("repo", "Arch-Dark"),
                         ("repo", "Debian-Dark"), ("repo", "Docker"),
                         ("si", "proxmox"), ("si", "nginx"), ("repo", "Grafana-Dark")],
    "stack-ai":         [("si", "ollama"), ("si", "vllm")],
    "stack-network":    [("si", "tailscale"), ("si", "wireguard")],
    "stack-hardware":   [("repo", "Arduino"), ("text", ("ESP32", "#F38BA8", 56)),
                         ("repo", "RaspberryPi-Dark")],
    "stack-design":     [("repo", "Blender-Dark"), ("si", "aseprite"),
                         ("si", "krita"), ("text", ("CSP", "#F5BDE6", 88)),
                         ("si", "davinciresolve"), ("repo", "Photoshop"),
                         ("repo", "AfterEffects")],
    "stack-maker":      [("si", "freecad"), ("si", "kicad"),
                         ("text", ("FUSION", "#7AA2F7", 44)),
                         ("text", ("KLIPPER", "#9ECE6A", 38)),
                         ("text", ("ORCA", "#FAB387", 62))],
    "stack-games":      [("repo", "Unity-Dark"), ("repo", "Godot-Dark"),
                         ("si", "steam")],
    # para añadir tus juegos favoritos:  ("si", "undertale"), ("si", "valorant")…
}

# iconos de juegos disponibles en simple-icons para añadir:
JUEGOS_SI = [
    "undertale", "leagueoflegends", "valorant", "counterstrike", "dota2",
    "epicgames", "playstation", "steamdeck", "itchdotio",
]


def _download(url):
    """urllib y, si falla, curl: raw.githubusercontent devuelve 404
    intermitente desde algunos entornos."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode()


def _download_curl(url):
    res = subprocess.run(["curl", "-sSfL", "--max-time", "30", url],
                         capture_output=True, text=True, check=True)
    return res.stdout


def fetch(url, tries=6):
    CACHE.mkdir(parents=True, exist_ok=True)
    cache = CACHE / url.split("/")[-1]
    if not cache.exists():
        for i in range(tries):
            for modo in (_download, _download_curl):
                try:
                    cache.write_text(modo(url))
                    break
                except Exception:
                    continue
            if cache.exists():
                break
            time.sleep(1.0 + i)   # 404 transitorio de GitHub raw
        else:
            raise RuntimeError(f"no se pudo descargar {url} tras {tries} intentos")
    return cache.read_text()


def repo_icon(name):
    """Tile oficial de skill-icons (ya viene con fondo y esquinas).

    Si el nombre exacto no existe, prueba las variantes -Dark / -Light
    (skill-icons nombra los iconos según el tema para el que son).
    """
    for intento in (name, name + "-Dark", name + "-Light"):
        try:
            svg = fetch(SKILL_REPO + intento + ".svg")
            return re.sub(r"<\?xml[^>]*\?>", "", svg).strip()
        except Exception:
            continue
    raise RuntimeError(f"no encuentro el icono de skill-icons: {name}")


def si_icon(slug):
    """(path, color) de un logo de simple-icons; blanco si es muy oscuro."""
    svg = fetch(f"{SIMPLE_ICONS}{slug}")
    d = re.search(r'<path[^>]*d="([^"]+)"', svg).group(1)
    fill = re.search(r'fill="(#[0-9A-Fa-f]{6})"', svg)
    fill = fill.group(1) if fill else "#FFFFFF"
    h = fill.lstrip("#")
    lum = (0.2126 * int(h[0:2], 16) + 0.7152 * int(h[2:4], 16)
           + 0.0722 * int(h[4:6], 16))
    return d, "#FFFFFF" if lum < 100 else fill


def si_tile(slug, x):
    d, fill = si_icon(slug)
    return (f'  <g transform="translate({x},0)">\n'
            f'    <rect width="256" height="256" rx="60" fill="#242938"/>\n'
            f'    <g transform="translate(48,48) scale(6.66667)"><path d="{d}" fill="{fill}"/></g>\n'
            f'  </g>')


def text_tile(txt, color, x, size):
    return (f'  <g transform="translate({x},0)">\n'
            f'    <rect width="256" height="256" rx="60" fill="#242938"/>\n'
            f'    <text x="128" y="128" text-anchor="middle" dominant-baseline="central" '
            f'font-family="ui-monospace,Menlo,Consolas,monospace" font-weight="bold" '
            f'font-size="{size}" fill="{color}">{txt}</text>\n'
            f'  </g>')


def mpl_tile(x):   # matplotlib: mini gráfica
    pts = "".join(f'<circle cx="{cx}" cy="{cy}" r="10" fill="#7DCFFF"/>'
                  for cx, cy in [(84, 182), (114, 138), (146, 166), (178, 92)])
    return (f'  <g transform="translate({x},0)">\n'
            f'    <rect width="256" height="256" rx="60" fill="#242938"/>\n'
            f'    <path d="M56 64 V200 H200" stroke="#F9E2AF" stroke-width="10" fill="none" stroke-linecap="round"/>\n'
            f'    <path d="M84 182 L114 138 L146 166 L178 92" stroke="#F38BA8" stroke-width="12" '
            f'fill="none" stroke-linecap="round" stroke-linejoin="round"/>{pts}\n  </g>')


def pygame_tile(x):  # pygame: serpiente pixel
    celdas = [(96, 176), (112, 176), (128, 176), (144, 176), (160, 176), (160, 160),
              (160, 144), (160, 128), (144, 128), (128, 128), (112, 128), (96, 128),
              (80, 128), (80, 112), (80, 96), (96, 96), (112, 96), (128, 96), (144, 96)]
    cuerpo = "".join(f'<rect x="{cx}" y="{cy}" width="16" height="16" fill="#6DC24B"/>'
                     for cx, cy in celdas)
    return (f'  <g transform="translate({x},0)">\n'
            f'    <rect width="256" height="256" rx="60" fill="#242938"/>{cuerpo}\n'
            f'    <rect x="148" y="100" width="8" height="8" fill="#FFFFFF"/>\n'
            f'    <rect x="160" y="88" width="8" height="8" fill="#F38BA8"/>\n  </g>')


def gym_tile(x):  # gymnasium: cart-pole
    return (f'  <g transform="translate({x},0)">\n'
            f'    <rect width="256" height="256" rx="60" fill="#242938"/>\n'
            f'    <rect x="62" y="222" width="132" height="6" fill="#4C557A"/>\n'
            f'    <rect x="88" y="176" width="80" height="24" fill="#F9E2AF"/>\n'
            f'    <rect x="96" y="200" width="16" height="16" fill="#7DCFFF"/>\n'
            f'    <rect x="144" y="200" width="16" height="16" fill="#7DCFFF"/>\n'
            f'    <rect x="121" y="58" width="14" height="120" fill="#7DCFFF" transform="rotate(18 128 178)"/>\n'
            f'    <circle cx="128" cy="176" r="12" fill="#F38BA8"/>\n  </g>')


DIBUJOS = {"mpl": mpl_tile, "pygame": pygame_tile, "gym": gym_tile}


def main():
    for nombre, items in STRIPS.items():
        tiles, n = [], len(items)
        for i, item in enumerate(items):
            x, kind = 300 * i, item[0]
            if kind == "repo":
                tiles.append(f'  <g transform="translate({x},0)">{repo_icon(item[1])}</g>')
            elif kind == "si":
                tiles.append(si_tile(item[1], x))
            elif kind == "text":
                tiles.append(text_tile(*item[1][:2], x, item[1][2]))
            elif kind == "draw":
                tiles.append(DIBUJOS[item[1]](x))
        W = 300 * n - 44
        capas = "\n".join(tiles)
        atenuado = ""
        if nombre in TENUE:
            capas = f'  <g opacity="{TENUE[nombre]}">\n{capas}\n  </g>'
            atenuado = f' (atenuado al {int(TENUE[nombre]*100)}%)'
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="256" '
               f'viewBox="0 0 {W} 256" fill="none">\n'
               f'<!-- {nombre} · iconos: skill-icons (tandpfun, MIT) + tiles propios -->\n'
               + capas + "\n</svg>\n")
        (OUT / f"{nombre}.svg").write_text(svg)
        print(f'{nombre}.svg: {n} tiles{atenuado} · <img src="./assets/{nombre}.svg" '
              f'width="{round(W * 49 / 256)}" height="49" alt="…"/>')
    print(f"\niconos de juegos disponibles en simple-icons: {', '.join(JUEGOS_SI)}")


if __name__ == "__main__":
    main()
