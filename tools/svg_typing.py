#!/usr/bin/env python3
"""
Motor de "máquina de escribir" en SVG puro (SMIL), compartido por
tools/generar_header.py y tools/generar_fastfetch.py.

Cómo funciona:
  · cada carácter es un <tspan opacity="0"> con su propio <animate
    opacity> que lo enciende al teclear;
  · el bloque del cursor es un <rect> con dos animaciones (<animate x> y
    <animate y>) sincronizadas con la escritura: avanza carácter a
    carácter y baja a cada línea;
  · el cursor va SOLIDO mientras escribe y solo parpadea durante las
    pausas (o sea, "al acabar");
  · al terminar una línea el cursor se queda un espacio en blanco por
    detrás del último carácter, como sihubieras pulsado espacio.

Los estados base son opacity="0": si un visor no soporta SMIL, no se ve
el texto en lugar de verse todo amontonado.
"""

ESC = {"&": "&amp;", "<": "&lt;", ">": "&gt;"}
esc = lambda s: "".join(ESC.get(c, c) for c in s)
fmt = lambda x: f"{x:.5f}"
MONO = "ui-monospace,Menlo,Consolas,monospace"


class Terminal:
    """Cronometra la escritura y devuelve el SVG de las líneas."""

    def __init__(self, ciclo, delta=0.0008, cursor_inicio=None, loop=True):
        self.ciclo = ciclo          # duración de un loop completo (s)
        self.loop = loop            # False = escribe una vez y se queda
        self.delta = delta          # margen de interpolación en keyTimes
        self.t = 0.0                # "reloj" de escritura
        self.pausas = []            # (inicio, fin) de cada descanso
        self.lineas = []            # SVG de cada <text>
        self.movs = []              # (tiempo, x, y) del cursor
        if cursor_inicio:           # el cursor arranca en otro sitio
            x, y = cursor_inicio
            self.movs.append((0.0, x, y))

    # ── una línea: segmentos = [(texto, color), ...] ────────────────────
    def linea(self, segmentos, x, y, size=13, dt=0.02, gap=0.12,
              cursor=True, attrs="", pausa=0.0, borrar=False, dt_del=0.03):
        """Escribe la línea, descansa `pausa` segundos y, si `borrar`,
        la borra de derecha a izquierda antes de la siguiente.

        El descanso se pinta justo después del último carácter, que es
        donde se para el cursor; `gap` es el margen hasta la línea
        siguiente.
        """
        chars, idx = [], 0
        for texto, color in segmentos:
            for ch in texto:
                chars.append((ch, color, idx))
                idx += 1
        n = len(chars)
        if n == 0:
            return self.t
        rep = 'indefinite' if self.loop else '1'
        frz = '' if self.loop else ' fill="freeze"'
        ancho = size * 0.6
        cy = y - size * 0.84          # borde superior del cursor en esta línea
        t_ini = self.t
        fin = t_ini + n * dt
        fin_pausa = fin + pausa       # el cursor se para aquí y parpadea
        t_borrado = fin_pausa
        partes = []
        for ch, color, i in chars:
            ta = t_ini + i * dt
            td = t_borrado + (n - 1 - i) * dt_del if borrar else self.ciclo
            a, d, dl = ta / self.ciclo, td / self.ciclo, self.delta
            val = "0;0;1;1;0;0" if borrar else "0;0;1;1;1"
            if a >= 2 * dl:
                kt = [0, a - dl, a, d - dl, d, 1] if borrar else [0, a - dl, a, 1 - dl, 1]
            else:
                kt = [0, dl, 2 * dl, d - dl, d, 1] if borrar else [0, dl, 2 * dl, 1 - dl, 1]
            partes.append(
                f'<tspan fill="{color}" opacity="0">'
                f'<animate attributeName="opacity" dur="{fmt(self.ciclo)}s" '
                f'repeatCount="{rep}"{frz} calcMode="linear" values="{val}" '
                f'keyTimes="{";".join(fmt(k) for k in kt)}"/>{esc(ch)}</tspan>')
        self.lineas.append(
            f'  <text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" '
            f'font-weight="bold" xml:space="preserve"{attrs}>{"".join(partes)}</text>')
        if cursor:
            for i in range(n):
                self.movs.append((t_ini + i * dt, x + i * ancho, cy))
            # un espacio en blanco detrás del texto
            self.movs.append((fin, x + (n + 1) * ancho, cy))
            if borrar:                    # el cursor retrocede al borrar
                for i in range(n - 1, -1, -1):
                    self.movs.append((t_borrado + (n - 1 - i) * dt_del, x + i * ancho, cy))
        self.t = fin + pausa + (n * dt_del if borrar else 0)
        if pausa > 0:
            self.pausas.append((fin, fin_pausa))
        return fin

    def cerrar(self, extra=0.0):
        """Cierra el ciclo: el resto hasta `ciclo` es la pausa final."""
        self.t += extra
        if self.t < self.ciclo:
            self.pausas.append((self.t, self.ciclo))
        if self.movs:
            self.movs.append((self.ciclo, self.movs[-1][1], self.movs[-1][2]))

    # ── cursor: mueve x e y, sólido al escribir y parpadeando al parar ───
    def cursor_svg(self, w=7, h=13, color="#7AA2F7", parpadeo=1.0, HOLDA=0.25):
        movs = []
        for t, x, y in self.movs:
            if movs:
                hueco = t - movs[-1][0]
                # en una pausa hay que "aguantar" la posición: sin este
                # keyframe extra, SMIL interpola y el cursor se desliza
                if hueco > HOLDA:
                    movs.append((t - 0.03, movs[-1][1], movs[-1][2]))
                elif t <= movs[-1][0]:
                    if abs(x - movs[-1][1]) < 1e-6 and abs(y - movs[-1][2]) < 1e-6:
                        continue
                    t = movs[-1][0] + 1e-5
            movs.append((t, x, y))
        if not movs:
            return ""
        movs[-1] = (self.ciclo, movs[-1][1], movs[-1][2])
        vals_x = ";".join(fmt(x) for _, x, _ in movs)
        vals_y = ";".join(fmt(y) for _, _, y in movs)
        times = ";".join(fmt(t / self.ciclo) for t, _, _ in movs)
        # opacidad: siempre visible, y 0/1 alternando DENTRO de cada pausa.
        # Ojo: hay que dejar un keyframe "1" justo al final de cada pausa;
        # si no, el 0 se extiende hasta la siguiente marca y el cursor
        # desaparece mientras escribe.
        op = [(0.0, 1)]
        for ini, fin in self.pausas:
            ini, fin = ini / self.ciclo, fin / self.ciclo
            if ini <= op[-1][0]:
                continue
            op.append((ini, 1))
            pasos = max(2, int((fin - ini) * self.ciclo / parpadeo) * 2)
            for i in range(pasos):
                t = ini + (fin - ini) * (i + 1) / (pasos + 1)
                if t > op[-1][0]:
                    op.append((t, 0 if i % 2 else 1))
            if fin > op[-1][0]:
                op.append((fin, 1))          # fuera de la pausa, visible
        if op[-1][0] < 1:
            op.append((1.0, 1))
        op_v = [str(val) for _, val in op]
        op_k = [fmt(t) for t, _ in op]
        # con loop=False la animación se congela al terminar (fill=freeze)
        rep = 'indefinite' if self.loop else '1'
        frz = '' if self.loop else ' fill="freeze"'
        return (f'  <rect x="{movs[0][1]}" y="{movs[0][2]}" width="{w}" height="{h}" '
                f'fill="{color}" opacity="0">\n'
                f'    <animate attributeName="x" dur="{fmt(self.ciclo)}s" '
                f'repeatCount="{rep}"{frz} values="{vals_x}" keyTimes="{times}"/>\n'
                f'    <animate attributeName="y" dur="{fmt(self.ciclo)}s" '
                f'repeatCount="{rep}"{frz} values="{vals_y}" keyTimes="{times}"/>\n'
                f'    <animate attributeName="opacity" dur="{fmt(self.ciclo)}s" '
                f'repeatCount="{rep}"{frz} calcMode="discrete" '
                f'values="{";".join(op_v)}" keyTimes="{";".join(op_k)}"/>\n'
                f'  </rect>')

    def svg_lineas(self):
        return "\n".join(self.lineas)
