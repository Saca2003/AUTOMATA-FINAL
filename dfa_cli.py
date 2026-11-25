# Automata de un pedido de comida por delivery.
# Adaptacion del generador del docente al diagrama del equipo.
import math
import sys

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Circle, FancyArrowPatch
from matplotlib.path import Path


# === Definicion del automata: coincide con el dibujo, sin bucle d ===
states = {
    "Inicio", "Carrito", "Metodo_pago", "Tarjeta", "Efectivo",
    "Preparacion", "Se_envia", "Entregado", "Cancelado"
}
alphabet = {"a", "b", "c"}
delta = {
    ("Inicio", "a"): "Carrito",
    ("Carrito", "a"): "Metodo_pago",
    ("Carrito", "b"): "Cancelado",
    ("Metodo_pago", "a"): "Tarjeta",
    ("Metodo_pago", "b"): "Efectivo",
    ("Metodo_pago", "c"): "Cancelado",
    ("Tarjeta", "a"): "Preparacion",
    ("Efectivo", "a"): "Preparacion",
    ("Preparacion", "a"): "Se_envia",
    ("Preparacion", "b"): "Cancelado",
    ("Se_envia", "a"): "Entregado",
}
q0, F = "Inicio", {"Entregado", "Cancelado"}


# === Simulacion ===
def run(s):
    q, steps = q0, [q0]
    for i, ch in enumerate(s):
        if ch not in alphabet:
            raise ValueError(
                f"Simbolo '{ch}' fuera del alfabeto en posicion {i + 1}. "
                "Utiliza solamente a, b y c."
            )
        if (q, ch) not in delta:
            raise ValueError(
                f"Sin transicion desde {q} con '{ch}' "
                f"en posicion {i + 1}."
            )
        q = delta[(q, ch)]
        steps.append(q)
    return steps, q in F


# === Grafo y posiciones fijas, similares al dibujo del equipo ===
pos = {
    "Inicio": (0.0, 4.0),
    "Carrito": (3.3, 4.0),
    "Metodo_pago": (6.6, 4.0),
    "Tarjeta": (10.0, 5.0),
    "Efectivo": (10.0, 3.0),
    "Preparacion": (10.0, 0.5),
    "Se_envia": (6.6, 0.5),
    "Entregado": (3.3, 0.5),
    "Cancelado": (0.0, 0.5),
}
labels = {
    "Inicio": "Inicio del\npedido",
    "Carrito": "Carrito",
    "Metodo_pago": "Método\nde pago",
    "Tarjeta": "Tarjeta",
    "Efectivo": "Efectivo",
    "Preparacion": "Preparación\ndel pedido",
    "Se_envia": "Se envía",
    "Entregado": "Pedido\nentregado",
    "Cancelado": "Pedido\ncancelado",
}
G = nx.MultiDiGraph()
G.add_nodes_from(pos)
for (source, symbol), target in delta.items():
    G.add_edge(source, target, key=symbol, label=symbol)

RADIUS = 0.78


def radius(state):
    return RADIUS + 0.10 if state in F else RADIUS


def draw_edge(ax, source, target, symbol):
    x1, y1 = pos[source]
    x2, y2 = pos[target]

    # La flecha de Tarjeta pasa por la derecha de Efectivo.
    if (source, target) == ("Tarjeta", "Preparacion"):
        vertices = [
            (x1 + radius(source), y1),
            (13.0, 4.8), (13.0, 0.7),
            (x2 + radius(target), y2),
        ]
        label_at = (12.55, 2.85)
    # La cancelacion desde Preparacion pasa debajo de los otros estados.
    elif (source, target) == ("Preparacion", "Cancelado"):
        vertices = [
            (x1, y1 - radius(source)),
            (8.5, -2.5), (1.5, -2.5),
            (x2, y2 - radius(target)),
        ]
        label_at = (5.0, -2.0)
    else:
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        ux, uy = dx / length, dy / length
        start = (x1 + radius(source) * ux, y1 + radius(source) * uy)
        end = (x2 - radius(target) * ux, y2 - radius(target) * uy)
        ax.add_patch(FancyArrowPatch(
            start, end, arrowstyle="-|>", mutation_scale=19,
            linewidth=1.8, color="#334155", shrinkA=2, shrinkB=2,
            zorder=1,
        ))
        label_at = (
            (start[0] + end[0]) / 2 - 0.20 * uy,
            (start[1] + end[1]) / 2 + 0.20 * ux,
        )
        vertices = None

    if vertices is not None:
        path = Path(vertices, [Path.MOVETO] + [Path.CURVE4] * 3)
        ax.add_patch(FancyArrowPatch(
            path=path, arrowstyle="-|>", mutation_scale=19,
            linewidth=1.8, color="#334155", zorder=1,
        ))
    ax.text(
        *label_at, symbol, ha="center", va="center",
        fontsize=13, fontweight="bold", color="#1d4ed8",
        bbox={"facecolor": "white", "edgecolor": "none", "pad": 2},
        zorder=4,
    )


def draw_step(current, idx, sym=None):
    fig = plt.figure("Autómata de delivery", figsize=(15, 8.8))
    ax = fig.gca()
    ax.clear()

    for source, target, data in G.edges(data=True):
        draw_edge(ax, source, target, data["label"])

    for state, (x, y) in pos.items():
        color = "#ffda88" if state == current else (
            "#dcfce7" if state in F else "#e0f2fe"
        )
        border = "#15803d" if state in F else "#075985"
        ax.add_patch(Circle(
            (x, y), RADIUS, facecolor=color,
            edgecolor=border, linewidth=2.5, zorder=2,
        ))
        if state in F:
            ax.add_patch(Circle(
                (x, y), radius(state), fill=False,
                edgecolor=border, linewidth=2, zorder=2,
            ))
        ax.text(
            x, y, labels[state], ha="center", va="center",
            fontsize=11, color="#0f172a", zorder=3,
        )

    ax.annotate(
        "", xy=(-RADIUS, 4.0), xytext=(-2.0, 4.0),
        arrowprops={"arrowstyle": "-|>", "color": "#334155", "lw": 2},
    )
    ax.text(-1.55, 4.25, "Inicio", ha="center", fontsize=10)
    suffix = f"  |  Símbolo: '{sym}'" if sym is not None else ""
    ax.set_title(
        f"Pedido de comida por delivery\nPaso {idx}: {labels[current].replace(chr(10), ' ')}{suffix}",
        fontsize=16, pad=14,
    )
    ax.text(
        5.4, -3.0,
        "Amarillo: estado actual   ·   Doble círculo: estado final\n"
        "Alfabeto: {a, b, c}   ·   Las transiciones no dibujadas se rechazan.",
        ha="center", va="center", fontsize=11, color="#475569",
    )
    ax.set_xlim(-2.3, 13.2)
    ax.set_ylim(-3.6, 6.3)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.canvas.draw_idle()
    return fig


def main():
    s = sys.argv[1] if len(sys.argv) > 1 else input("Cadena (a/b/c): ").strip()
    try:
        steps, ok = run(s)
    except ValueError as error:
        print("RECHAZA:", error)
        return

    print("ACEPTA" if ok else "RECHAZA", f"(estado final: {steps[-1]})")
    print("Recorrido:", " -> ".join(steps))
    plt.ion()
    draw_step(steps[0], 0)
    plt.pause(1.0)
    for i, ch in enumerate(s, 1):
        draw_step(steps[i], i, ch)
        plt.pause(1.0)
    plt.ioff()
    plt.show()


if __name__ == "__main__":
    main()
