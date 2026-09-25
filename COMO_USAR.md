# 🖥️ COMO_USAR · Perfil "una sesión de terminal"

README de perfil con estética **terminal pura**: toda la página se lee como
**una sola sesión de shell** y cada sección es un comando:

```
fastfetch → tree ~/stack → nmap -sV daviddans → exit 0
```

Todo el arte (cabecera, pie, divisores, sprites, tiles de iconos) son
**SVG animados propios** en `assets/` — cero plantillas vistas en otros
perfiles, y sin depender de servicios externos para la decoración.

## 🎨 1 · La paleta "SynthNight Mocha"

**Tokyo Night** de fondo, acentos pastel **Catppuccin Mocha**, energía
**synthwave** (sol, rejilla en perspectiva, ondas).

| Color | Hex | Usos |
|:---|:---|:---|
| fondo | `#1A1B26` | cabecera, pie, chip, gato |
| ♥ rojo pastel | `#F38BA8` | corazón, café, esp32, FavColor, error del pie |
| lila | `#CBA6F7` | cursor, fantasma, homelab, hackudc |
| azul | `#7AA2F7` | prompt, gato, arch, rejilla |
| cian | `#7DCFFF` | chip, LLMs, pole del cart-pole, rejilla |
| verde éxito | `#9ECE6A` | "exit 0", active(running), neovim |
| ámbar | `#F9E2AF` | estrella, RL, pixel art, sol |
| melocotón | `#FAB387` | café, TFG, próxmox-tile, sol |
| rosa suave | `#F5BDE6` | orejas del gato, FIC·UDC, CSP, diseño |

> Regla del rojo: solo en lo que te define (♥, café) y en el error final.

## 🗂️ 2 · Mapa de secciones

| Elemento | Qué hay |
|:---|:---|
| `assets/header.svg` | cabecera original: prompt + escena synthwave **+ el typing animado dentro** (SMIL, sin servicios externos) |
| `$ fastfetch` + `cat ./about_me.md` | el panel, a todo el ancho y **reactivo** (estrecho en móvil / ancho en escritorio) |
| etiquetas | tabla propia a todo el ancho: 29 tags en 3 columnas + fila de sprites |
| `assets/divider-wave.svg` | **el único divisor** (onda + burbujas, estrecho y a todo el ancho) |
| `$ tree ~/stack/ -L 2` | stack en strips de iconos uniformes, 13 carpetas |
| `assets/divider-wave.svg` | el mismo divisor, otra vez |
| `$ nmap -sV -T4 daviddans` | contacto: `assets/nmap.svg` (5 puertos inventados = tus 5 redes) + badges clicables |
| `assets/footer.svg` | pie: `exit 0` + `logout` + `[ERROR] social_life: process not found` |

El hilo narrativo es una sesión de terminal de principio a fin:
**`whoami` → `fastfetch` → `tree` → `nmap` → `exit 0`**. Por eso el pie
vuelve a cerrar con el mismo prompt que la cabecera.

Separador **único**: la onda (`divider-wave.svg`), repetida en los dos
cortes que quedan. Es estrecho (viewBox 900×56) pero va con
`width="100%"`, así que ocupa siempre todo el ancho del README.

## 📺 3 · El panel "fastfetch" (hero)

**Ya no es un widget externo**: es `assets/fastfetch.svg` +
`assets/fastfetch-wide.svg`, generados por
`tools/generar_fastfetch.py`. ¿Por qué? Porque el widget
(github-stats-terminal-style) no permite logo propio ni pausas: su
`neofetch` lleva el logo de GitHub fijo en el código y no existe comando
`sleep`. Al hacerlo nosotros tenemos:

- **logo de Arch** junto a las líneas `key: value`
- **tecleo carácter a carácter** (SMIL), más rápido que el widget
- **10 s de pausa** al final para leerlo todo
- cero dependencias externas (se ve igual en GitHub, GitLab, Codeberg…)

| Parámetro (en el script) | Qué hace |
|:---|:---|
| `FASTFETCH` | lista `(etiqueta, valor)` del `fastfetch` |
| `ABOUT` | líneas de `cat ./about_me.md` (la primera es el encabezado) |
| `DT_TEXTO` / `DT_PROMPT` | velocidad del tecleo (s por carácter) |
| pausas del guion | cada línea del plan lleva su `gap` y su `pausa` (descanso entre bloques) |
| `PAUSA` | segundos de lectura al final, antes de reiniciar (10) |
| `CUENTA` | fecha de creación de la cuenta → calcula el `uptime` |
| `VARIANTES` | geometría de cada versión: `estrecha` (420×452, una columna) y `ancha` (780×323, `AX` = columna del `about_me.md`) |

El guion de la sesión es: **`fastfetch` → `cat ./about_me.md` → `uptime`
→ `exit`**, y al final se queda 10 s quieto para poder leerlo.

```bash
python3 tools/generar_fastfetch.py
```

> Truco al ajustar el tamaño: el panel se dibuja en la columna izquierda
> (45% del README), así que lo que ves es `(TAM / W) × ancho_de_la_columna`.
> Con `W=420` y `TAM=11` la fuente sale ~12 px en pantalla.

Los datos vivos de GitHub que daba el widget (uptime, followers…) siguen
estando: **followers y stars** son badges dinámicas de shields en la
sección de repos, y la racha es la de streak-stats.

### El panel es "reactivo" (con las limitaciones del markdown)

No hay foto: el panel ocupa todo el ancho. Y como en el README **no hay
CSS**, la única cosa "reactiva" posible es **cambiar de imagen según el
ancho**, que se hace con `<picture>`:

```html
<picture>
  <source media="(max-width: 700px)" srcset="./assets/fastfetch.svg">   <!-- móvil -->
  <img src="./assets/fastfetch-wide.svg" width="100%">                  <!-- escritorio -->
</picture>
```

O sea: **sí** se puede adaptar la imagen al ancho (y por eso hay dos
versiones del panel, con el mismo guion y la misma animación), pero **no**
se puede reordenar la maquetación: si quisieras esconder *una celda* en
móvil y sacar *otra* en escritorio, eso no se puede. Por eso el avatar se
fue en lugar de esconderse.

### Las etiquetas (y por qué NO están junto a la foto)

Los 29 tags van en **su propia tabla a todo el ancho**, en **tres
columnas**: `~/identidad` + `~/.soft-skills` | `~/.hobbies/tech` |
`~/.hobbies`. Y la fila de sprites va debajo, centrada.

> ⚠️ **Por qué están fuera de la tabla del hero** (esto costó una
> subida): desde 2023 GitHub **dibuja un borde en cada `<td>`** y reparte
> el ancho de la tabla según lo que **pide** cada celda. Con los tags
> dentro de la celda de la foto, aquella celda pedía 590 px, el panel se
> quedaba a 240 px (el texto, ilegible) y su celda se pintaba como un
> **rectángulo vacío de 700 px** debajo del panel. Arriba del todo, la
> tabla del hero solo lleva el panel y la foto, y los tags van en su
> propia tabla: así cada celda pide lo que le corresponde y no queda
> hueco. Mi preview local (`tools/test-hero.py`) reproduce a propósito
> el CSS de GitHub (bordes + `display:block`) para que esto se viera sin
> subirlo.

Generado por `tools/generar_tags.py` (`IDENTIDAD`, `TECH`, `OFFLINE`,
`SOFT`, y `COL` = ancho máximo de fila, 272 px). Cada grupo se emite como
un `<p align="center">` con las filas separadas por `<br/>`, **no** como
una tabla interna: anidar tablas metía unas 40 cajitas alrededor de cada
badge, porque GitHub las bordea igual.

**Dos reglas de shields.io que aprendimos a base de romper cosas:**

1. Los emoji **sí** funcionan (miden el glifo), pero **un guion (`-`) en
   el texto junto a un emoji rompe la URL**: shields separa el path por
   guiones y responde *"404 badge not found"*. Usa "selfhosting", no
   "self-hosting".
2. El `&` va **codificado** (`%26`) y en los `alt` del HTML como
   `&amp;`.

Por eso el generador, al terminar, **valida cada badge contra shields** y
avisa de las que estén rotas. Los anchos se calculan con la fórmula real
(5,12 px por carácter + 31 px) para repartir las filas.

## 🌲 4 · El stack (strips de iconos propios)

Cada carpeta del tree muestra un **strip SVG** (`assets/stack-*.svg`):
tiles uniformes de 256px (esquinas rx 60, gap 44) — la misma geometría que
skill-icons. Composición:

- **Tiles de skill-icons** (repo tandpfun, MIT): C, C# (`CS`), Python, Java,
  Bash, JS, TS, Flutter, Git, VS Code, Visual Studio, .NET, React, Next.js,
  PyTorch, Linux, Arch, Debian, Docker, Arduino, Blender, Unity, Godot.
- **Tiles con logos de simple-icons** (los que skill-icons no tiene):
  erlang, lazyvim, numpy, proxmox, ollama, vLLM, aseprite, krita,
  DaVinci Resolve, steam.
- **Tiles dibujados a mano**: matplotlib (gráfica), pygame (serpiente pixel),
  gymnasium (cart-pole) y de texto: `SB3`, `ESP32`, `CSP`.

| Strip | Contenido |
|:---|:---|
| `stack-langs.svg` | C · C++ · C# · Python · Java · Bash |
| `stack-learning.svg` | JS · TS · Flutter · Erlang · Lua *(atenuado)* |
| `stack-tools.svg` | git · VS Code · Visual Studio · LazyVim · Alacritty · Zellij · Obsidian |
| `stack-frameworks.svg` | .NET · React · Next.js · FastAPI · Spring |
| `stack-pylibs.svg` | NumPy · Matplotlib · Pygame |
| `stack-ml.svg` | PyTorch · scikit-learn · Hugging Face · Gymnasium · Stable-Baselines3 |
| `stack-infra.svg` | Linux · Arch · Debian · Docker · Proxmox · NGINX · Grafana |
| `stack-ai.svg` | Ollama · vLLM |
| `stack-network.svg` | Tailscale · WireGuard |
| `stack-hardware.svg` | Arduino · ESP32 · Raspberry Pi |
| `stack-design.svg` | Blender · Aseprite · Krita · Clip Studio · DaVinci Resolve · Photoshop · After Effects |
| `stack-maker.svg` | FreeCAD · KiCad · Fusion 360 · Klipper · Orca |
| `stack-games.svg` | Unity · Godot · Steam |

> **Límite de anchura**: cada tile mide **57 px** de ancho a 49 px de alto,
> así que en una columna del 50% caben **7 tiles**. Si te pasas, hay que
> partir en subcarpetas (por eso `infra/` tiene `ai/` y `network/`).

**Strips atenuados.** En `tools/generar_strips.py`:

```python
TENUE = {"stack-learning": 0.55}     # strips atenuados
```

envuelve el strip entero en un `<g opacity="…">`, así el bloque
`learning/` se lee "en proceso" sin escribirlo. Para añadir un folder
atenuado, su nombre a la lista y tira el generador.

**Editar / añadir tiles**: lo normal es usar el generador (§11):

```bash
python3 tools/generar_strips.py     # reconstruye los 9 strips e imprime
                                    # el <img width="…"> para el README
```

Ahí editas la lista `STRIPS` (p. ej. `("si", "steamdeck")` para un juego).
A mano también puedes: cada tile es un `<g transform="translate(…)">`; los de
texto cambian su `<text>`, y para un logo nuevo de simple-icons el tile es:
```svg
<g transform="translate(X,0)">
  <rect width="256" height="256" rx="60" fill="#242938"/>
  <g transform="translate(48,48) scale(6.66667)">
    <path d="…ruta de cdn.simpleicons.org/SLUG…" fill="#FFFFFF"/>
  </g>
</g>
```
y amplía el `viewBox`/`width` (+300 por tile). El `<img>` del README lleva
`width`/`height` proporcionales (49px de alto).

**Iconos de juegos disponibles** (simple-icons, verificados) para añadir
tus favoritos a `stack-games.svg`: undertale, leagueoflegends, valorant,
counterstrike, dota2, epicgames, playstation, steamdeck, itchdotio.

## ✏️ 5 · Qué queda por editar

**No queda ningún placeholder.** El contacto está completo y verificado:

| Red | Enlace | Cómo se comprobó |
|:---|:---|:---|
| GitHub | `github.com/daviddans` | — |
| Mail | `dans.villares@gmail.com` | badge del propio perfil de GitHub |
| LinkedIn | `linkedin.com/in/daviddans` | badge del propio perfil de GitHub |
| Steam | `steamcommunity.com/id/Daviddans` | API de la comunidad: perfil público, `steamID64 76561198192098301` |
| Instagram | `instagram.com/daviddans` | ⚠️ **sin poder verificar**: Instagram devuelve la misma página para cualquier usuario y no está en los índices de búsqueda. Es el handle que dio el autor; si fuera otro, cámbialo (ver abajo) |

> Cada red aparece **dos veces**: en las badges del README (clicables) y
> dentro del SVG del nmap (que es una imagen y no se puede pulsar). Si
> cambias alguna, cámbiala en los dos sitios y relanza
> `python3 tools/generar_nmap.py`.

Ya son tuyos: avatar (github.com/daviddans.png), quote, fastfetch/about_me
con tu info, el stack de 13 carpetas, las 29 etiquetas (identidad +
hito + hobbies + soft skills, todas bajo la foto) y la sesión de contacto
final. La sección de repos, racha y métricas se borró por quedar
redundante con el stack: si algún día quieres volver a enseñar el TFG,
el sitio natural es `tools/generar_fastfetch.py` (`ABOUT`) o una fila del
árbol del stack.

## 🌐 6 · Multi-plataforma (GitLab, Codeberg…)

- Todo es **HTML estándar + imágenes**: tablas, `<details>` y rutas
  relativas `./assets/` funcionan en cualquier forja.
- Cabecera, pie, divisores, sprites e **iconos del stack son archivos
  locales** → se ven idénticos en todas partes, sin proxy de por medio.
- Lo único que sale de un servicio externo son las **badges de
  shields.io** (las 29 del hero y las 3 de contacto). Shields se ve igual
  en GitLab, Codeberg o donde sea: son imágenes normales.
- Todo lo demás (`header`, `fastfetch`, `stack-*`, `nmap`, `footer`) son
  **archivos del repo**: sin SMIL se ven estáticos pero completos, y sin
  conexión se ven igual. Eso incluye las animaciones: si un visor no las
  soporta, el texto aparece entero en vez de amontonado.

## 🖼️ 7 · Decoraciones (`assets/`)

| Archivo | Qué es | Animación |
|:---|:---|:---|
| `header.svg` | cabecera: prompt + sol/rejilla synthwave + **typing que se escribe y se borra** | tecleo, parpadeo en la pausa, borrado de la frase, cursor que avanza, estrellas, rejilla |
| `footer.svg` | pie: `exit 0` + `logout` + `[ERROR] social_life` rojo | dos cursores parpadeando (lila y rojo) |
| `divider-wave.svg` | **el único separador** (onda doble + burbujas, 900×56) | morph del trazo, burbujas subiendo |
| `pixel-cat.svg` `pixel-chip.svg` `pixel-coffee.svg` `pixel-floppy.svg` `pixel-heart.svg` `pixel-star.svg` `pixel-coin.svg` `pixel-ghost.svg` | sprites pixel | rabo del gato, parpadeo, vapor, etiquetas, latido, titileo, flotado |
| `stack-*.svg` | strips de iconos (ver sección 4) | — (estáticos) |
| `nmap.svg` | el escaneo de puertos del final | tecleo una vez y el cursor se queda parpadeando |
| `fastfetch-wide.svg` | la versión ancha del panel del hero (escritorio) | igual que la estrecha, con el `about_me.md` en 2ª columna |

Para retocar: son `<rect>`/`<path>` con `<animate>`; cambia `fill` o `dur`.
**Excepción**: el typing de la cabecera NO se edita a mano (son 110 `<tspan>`
con su `<animate>`), se cambia en el generador (§10).

## ⚙️ 8 · Lo único que viene de fuera

| Recurso | Dónde | Estado |
|:---|:---|:---|
| badges de etiquetas (shields.io, `flat-square`, 24 px) | hero y contacto | ✅ funciona, y es lo único externo |
| todo lo demás | — | ✅ **local**: SVG del repo, sin servicios |

> **Por qué no hay ningún widget de estadísticas**: `github-readme-stats`
> (top-langs), `activity-graph` y `trophy` los hospeda alguien en el plan
> gratuito de Vercel. Cuando esa persona se pasa de cuota, mueren **para
> todo el mundo** y no hay nada que arreglar desde el README. Se llegaron
> a probar y estaban caídos (402/503), así que se quitaron: la sección de
> repos, racha y métricas se borró entera por redundante con el stack.
> Si algún día los quieres de vuelta, la forma buena es
> `lowlighter/metrics` como Action (genera los SVG y los commitea en tu
> repo, así que no se cae nunca); la mala es volver a apuntar a Vercel.

## 🚀 9 · Subirlo a tu perfil

1. Crea un repo público llamado **daviddans** (tu username exacto).
2. Copia `README.md`, `assets/` y `tools/`, haz push.
3. Rellena los dos placeholders del contacto (§5) y regenera el nmap:
   `python3 tools/generar_nmap.py`.
4. Listo. No hay ningún Action que lanzar ni ningún secreto que crear:
   **todo el perfil es estático**.

## 🧰 10 · Los generadores (`tools/`)

Scripts sin dependencias (solo Python 3) que reconstruyen los SVG
complicados a partir de listas legibles:

| Script | Qué genera | Se edita |
|:---|:---|:---|
| `tools/generar_header.py` | `assets/header.svg` (prompt + escena + **typing que se borra**) | `PROMPT`, `LINEAS` (texto+color), `DT`/`PAUSA`/`DT_DEL`/`GAP`, `TYPE_FONT` |
| `tools/svg_typing.py` | motor de tecleo **compartido** por cabecera, panel y nmap | — |
| `tools/generar_fastfetch.py` | `assets/fastfetch.svg` (panel del hero con logo Arch + pausa) | `FASTFETCH`, `ABOUT`, `CUENTA` (fecha de la cuenta para el `uptime`), `DT_TEXTO`/`DT_PROMPT`, `PAUSA`, geometría |
| `tools/generar_nmap.py` | `assets/nmap.svg` (el nmap de contacto) | `PUERTOS` (los 5 puertos), `DT`, `PAUSA`, `TAM`, `LSTEP` |
| `tools/generar_tags.py` | las 29 etiquetas del hero (HTML entre `BEGIN/END TAGS`) | `IDENTIDAD`, `TECH`, `OFFLINE`, `SOFT` |
| `tools/generar_strips.py` | los 13 `assets/stack-*.svg` | `STRIPS` (qué iconos va en cada carpeta) |
| `tools/preview.py` | `/tmp/opencode/preview/index.html` (assets inlineados) | — |
| `tools/test-hero.py` | `tools/test-hero.html`: hero con CSS estilo GitHub, sin marked.js | — |
| `tools/test-panel.html` · `test-header.html` · `test-nmap.html` | fotogramas congelados (`pauseAnimations` + `setCurrentTime`) | — |

```bash
python3 tools/generar_header.py    # ~instantáneo
python3 tools/generar_fastfetch.py # panel del hero (~1 s)
python3 tools/generar_nmap.py       # el nmap de contacto (~1 s)
python3 tools/generar_strips.py    # necesita red la 1ª vez (descarga logos)
python3 tools/preview.py           # render local del README

# para ver las animaciones fotograma a fotograma:
python3 -m http.server 8765        # y abre /tools/test-header.html
#                                    # o /tools/test-nmap.html
```

Notas:
- El typing del header se hace con **SMIL**: cada carácter es un `<tspan>`
  con `<animate opacity>` (se enciende al teclear y se apaga al borrar) y
  el bloque del cursor se mueve con un `<animate x>` sincronizado. Ciclo
  actual ≈ 17 s. Al añadir taglines, manténlos ≤ 40 caracteres: la zona
  de texto acaba antes de la escena synthwave (x≈640).
- El typing del header se hace con **SMIL** mediante el motor compartido
  `tools/svg_typing.py`. Ciclo actual ≈ 35 s: 5 frases × (teclear ~0,8 s +
  **5 s de pausa** + borrado). Se edita en `LINEAS`.
- Details del motor (importantes si lo tocas):
  - cada carácter es un `<tspan>` con su `<animate opacity>`;
  - el cursor es un `<rect>` con `<animate x>` **e `<animate y>`**: avanza
    carácter a carácter y baja de línea;
  - **SMIL interpola entre keyTimes**, así que en cada pausa se mete un
    keyframe extra con la posición repetida: si no, el cursor se desliza
    de vuelta al inicio mientras "descansa";
  - el cursor va **sólido** escribiendo y **parpadea** en las pausas
    (`parpadeo=1.0` = 1 s por ciclo);
  - al acabar una frase el cursor se queda **un espacio en blanco** por
    detrás del último carácter;
  - los `<tspan>` llevan `opacity="0"` como estado base: si un visor **no**
    soporta SMIL, el typing no se ve en lugar de verse todo amontonado.
- `Terminal(ciclo, loop=False)` = escribe **una vez** y se congela
  (`fill="freeze"`): es lo que usa `generar_nmap.py`, porque es la última
  cosa del perfil y si te quedas a medio bajar no quieres perderte el
  texto. El cursor del nmap añade encima un parpadeo infinito que empieza
  al terminar la escritura. Con `loop=True` (por defecto, cabecera y
  panel) hace lo de siempre: ciclo infinito.
- El **panel del hero** y el **nmap** van un paso más allá: llevan
  una **capa estática** (el texto plano, completo) que SMIL oculta. Así,
  si algo rasteriza el SVG sin animaciones, se ve el bloque entero en vez
  de un rect vacío.
- `generar_strips.py` cachea los logos descargados en
  `tools/.cache-iconos/` (no hace falta subirla al repo) y reimprime el
  `<img width="…">` exacto para cada strip.

## 🙏 Créditos

badges (shields.io) · logos (simple-icons) · tiles de skill-icons
(tandpfun, MIT). Cabecera, panel del hero, nmap, pie, divisores,
sprites y tiles dibujados: hechos para esta plantilla, sin depender de
nadie.
