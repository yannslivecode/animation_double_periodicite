# -*- coding: utf-8 -*-
"""
Mini-quiz « même courbe, deux lectures » (blocage 1.1).

Reproduit l'erreur type : « deux crêtes séparées de 4, donc λ = 4 ms ».
Deux graphes strictement identiques, axe horizontal masqué.
L'élève doit nommer l'axe AVANT de mesurer ; le bouton « Révéler »
montre que le même « 4 » vaut T = 4 ms sur s(t) et λ = 4 cm sur y(x).

Sous matplotlib < 3.5 (pas d'interactif en têteless), lancer avec :
    python quiz_deux_lectures.py
En salle machine interactif : une fenêtre s'ouvre avec le bouton.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button

U_MAX = 16
MOTIF = 4

u = np.linspace(0, U_MAX, 800)
s = np.cos(2 * np.pi * u / MOTIF)

fig, (a, b) = plt.subplots(1, 2, figsize=(13, 5.5))
for ax, ylab in ((a, "s"), (b, "y")):
    ax.plot(u, s, lw=2.5, color="tab:blue")
    ax.axhline(0, color="gray", lw=0.8)
    ax.set_xlim(0, U_MAX)
    ax.set_ylim(-1.6, 1.9)
    ax.set_ylabel(ylab, fontsize=13)
    ax.set_xlabel(
        "axe horizontal : ??? ", fontsize=13, color="crimson", fontweight="bold"
    )
a.set_title("Graphe A", fontsize=14)
b.set_title("Graphe B", fontsize=14)

fig.suptitle(
    "Dans les deux cas, deux motifs identiques consécutifs sont séparés de « 4 ».\n"
    "Que représente ce 4 ?  Nomme d'abord l'axe horizontal !",
    fontsize=13, fontweight="bold",
)


def reveal(event):
    # Graphe A : s(t), t en ms -> période temporelle
    a.set_title("Graphe A : $s(t)$ — VIDÉO d'un point",
                fontsize=14, color="tab:purple")
    a.set_xlabel("t (ms)", fontsize=13, color="tab:purple", fontweight="bold")
    a.annotate("", xy=(MOTIF, 1.3), xytext=(0, 1.3),
               arrowprops=dict(arrowstyle="<->", color="tab:purple", lw=2.5))
    a.text(MOTIF / 2, 1.42, "T = 4 ms", ha="center", color="tab:purple",
           fontsize=15, fontweight="bold")
    # Graphe B : y(x), x en cm -> période spatiale
    b.set_title("Graphe B : $y(x)$ — PHOTO de la corde",
                fontsize=14, color="tab:green")
    b.set_xlabel("x (cm)", fontsize=13, color="tab:green", fontweight="bold")
    b.annotate("", xy=(MOTIF, 1.3), xytext=(0, 1.3),
               arrowprops=dict(arrowstyle="<->", color="tab:green", lw=2.5))
    b.text(MOTIF / 2, 1.42, "λ = 4 cm", ha="center", color="tab:green",
           fontsize=15, fontweight="bold")
    fig.canvas.draw_idle()


plt.tight_layout(rect=[0, 0.12, 1, 0.9])
ax_btn = fig.add_axes([0.40, 0.02, 0.20, 0.07])
btn = Button(ax_btn, "Révéler l'axe horizontal")
btn.on_clicked(reveal)

if __name__ == "__main__":
    import os
    if os.environ.get("DISPLAY") or os.environ.get("ALLOW_GUI"):
        plt.show()
    else:
        # Mode headless : révélation automatique + export PNG pour projection
        reveal(None)
        fig.savefig("quiz_deux_lectures.png", dpi=150)
        print("Quiz écrit dans quiz_deux_lectures.png (axes révélés)")
