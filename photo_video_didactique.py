# -*- coding: utf-8 -*-
"""
Animation « photo / vidéo » — version didactique (blocage 1.1).

Objectif : empêcher la confusion « je lis λ sur un graphe s(t) ».
L'axe horizontal est l'objet central de l'animation :
  - vert  = espace (x, λ, mètres)  ;
  - violet = temps (t, T, secondes) ;
  - rouge = point M suivi simultanément sur les deux panneaux.
La routine de lecture est affichée dans un bandeau dédié SOUS les
graphiques (aucune superposition avec l'animation), aux côtés du
bouton Pause / Reprendre.
"""

import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import ConnectionPatch
from matplotlib.widgets import Button

# ---------- Paramètres (modifiables) ----------
A, LAM, T = 2.0, 0.40, 2.0      # amplitude (cm), λ (m), T (s)
V = LAM / T                     # célérité (m/s)
L = 1.20                        # longueur de corde affichée (m)
X_M = 0.50                      # position de M (m)
T_MAX, FPS = 10.0, 30

C_LAM, C_T, C_M = "tab:green", "tab:purple", "tab:red"


def y(x, t):
    return A * np.cos(2 * np.pi * (t / T - x / LAM))


# ---------- Figure ----------
fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(14, 6.5), gridspec_kw={"width_ratios": [1.1, 1]}
)
fig.suptitle(
    "Une onde périodique a DEUX périodes : "
    "l'une dans l'espace (λ), l'autre dans le temps (T)",
    fontsize=14, fontweight="bold",
)
YLIM = 1.9 * A
H = 1.35 * A

# Espace réservé aux bandeaux : les graphiques ne descendent jamais
# sous y = 0.24 de la figure, donc rien ne se superpose à l'animation.
fig.subplots_adjust(
    left=0.06, right=0.98, top=0.86, bottom=0.24, wspace=0.25
)


def style_axe_horizontal(ax, couleur, texte):
    """Met en évidence l'axe horizontal : c'est LUI qui décide de ce qu'on mesure."""
    ax.set_xlabel(texte, fontsize=13, fontweight="bold", color=couleur)
    ax.xaxis.label.set_bbox(
        dict(boxstyle="round,pad=0.3", fc="white", ec=couleur, lw=2)
    )
    ax.tick_params(axis="x", colors=couleur, labelsize=11)
    ax.spines["bottom"].set_color(couleur)
    ax.spines["bottom"].set_linewidth(3)


# ----- Gauche : la « photo » y(x) -----
x = np.linspace(0, L, 600)
ax1.set_xlim(0, L)
ax1.set_ylim(-YLIM, YLIM)
ax1.set_ylabel("y (cm)", fontsize=12)
style_axe_horizontal(ax1, C_LAM, "x (m)   →   axe des DISTANCES   →   on mesure λ")
ax1.axhline(0, color="gray", lw=0.8)
ax1.axvline(X_M, color=C_M, ls=":", lw=1)
corde, = ax1.plot([], [], color="tab:blue", lw=2.5)
M1, = ax1.plot([], [], "o", color=C_M, ms=13, zorder=5)
ax1.text(X_M, -YLIM * 0.93, "M", color=C_M, ha="center",
         fontsize=13, fontweight="bold")
titre1 = ax1.set_title("", fontsize=12)

fl_lam = ax1.annotate(
    "", xy=(0, H), xytext=(0, H),
    arrowprops=dict(arrowstyle="<->", color=C_LAM, lw=2.5),
)
txt_lam = ax1.text(
    0, H + 0.1 * A, f"λ = {LAM * 100:.0f} cm", color=C_LAM,
    ha="center", fontsize=14, fontweight="bold",
)
crete1, = ax1.plot([], [], color=C_LAM, ls="--", lw=1)
crete2, = ax1.plot([], [], color=C_LAM, ls="--", lw=1)

# ----- Droite : la « vidéo » y_M(t) -----
ax2.set_xlim(0, T_MAX)
ax2.set_ylim(-YLIM, YLIM)
ax2.set_ylabel("$y_M$ (cm)", fontsize=12)
style_axe_horizontal(ax2, C_T, "t (s)   →   axe des DURÉES   →   on mesure T")
ax2.axhline(0, color="gray", lw=0.8)
trace, = ax2.plot([], [], color=C_M, lw=2.5)
M2, = ax2.plot([], [], "o", color=C_M, ms=13, zorder=5)
ax2.set_title(
    f"VIDÉO du seul point M (x = {X_M * 100:.0f} cm) : $y_M(t)$", fontsize=12
)

t1 = (X_M / V) % T          # premier maximum de y_M
t2 = t1 + T
fl_T = ax2.annotate(
    "", xy=(t2, H), xytext=(t1, H),
    arrowprops=dict(arrowstyle="<->", color=C_T, lw=2.5),
)
txt_T = ax2.text(
    (t1 + t2) / 2, H + 0.1 * A, f"T = {T:.1f} s", color=C_T,
    ha="center", fontsize=14, fontweight="bold",
)
tm1, = ax2.plot([t1, t1], [0, H], color=C_T, ls="--", lw=1)
tm2, = ax2.plot([t2, t2], [0, H], color=C_T, ls="--", lw=1)
arts_T = (fl_T, txt_T, tm1, tm2)
for a in arts_T:
    a.set_visible(False)

# lien M (gauche) -> M (droite) : c'est le même mouvement
lien = ConnectionPatch(
    xyA=(X_M, 0), coordsA=ax1.transData,
    xyB=(0, 0), coordsB=ax2.transData,
    color=C_M, ls="--", lw=1, alpha=0.6,
)
fig.add_artist(lien)

# ----- Bandeau « routine » : zone DÉDIÉE sous les graphiques -----
fig.text(
    0.5, 0.115,
    "ROUTINE :  ① Je nomme l'axe horizontal   ②  x (m) → λ    ;    t (s) → T"
    "   ③ Je mesure entre deux motifs identiques",
    ha="center", va="center", fontsize=12, fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.5", fc="lightyellow", ec="goldenrod"),
)

# ----- Bouton Pause / Reprendre -----
ax_btn = fig.add_axes([0.42, 0.02, 0.16, 0.06])
ax_btn.set_facecolor("lightgray")
btn = Button(ax_btn, "Pause")
ETAT = {"i": 0, "pause": False}


def bascule_pause(event):
    ETAT["pause"] = not ETAT["pause"]
    btn.label.set_text("Reprendre" if ETAT["pause"] else "Pause")


btn.on_clicked(bascule_pause)

# ---------- Animation ----------
ts = np.arange(0, T_MAX, 1 / FPS)
yM_hist_full = y(X_M, ts)

def dessine(i):
    t = ts[i]
    corde.set_data(x, y(x, t))
    yM = y(X_M, t)
    M1.set_data([X_M], [yM])
    titre1.set_text(f"PHOTO de toute la corde à t = {t:.2f} s : $y(x)$")

    x1 = LAM * ((t / T) % 1)
    x2 = x1 + LAM
    fl_lam.xy = (x2, H)
    fl_lam.set_position((x1, H))
    txt_lam.set_position(((x1 + x2) / 2, H + 0.1 * A))
    crete1.set_data([x1, x1], [0, H])
    crete2.set_data([x2, x2], [0, H])

    trace.set_data(ts[: i + 1], yM_hist_full[: i + 1])
    M2.set_data([t], [yM])
    lien.xy1 = (X_M, yM)
    lien.xy2 = (t, yM)

    if t >= t2:
        for a in arts_T:
            a.set_visible(True)


def update(_frame):
    """En pause, l'indice ne progresse plus : l'image est figée."""
    if not ETAT["pause"]:
        ETAT["i"] += 1
        if ETAT["i"] >= len(ts):
            ETAT["i"] = 0          # reboucle pour la projection en classe
            for a in arts_T:
                a.set_visible(False)
    dessine(ETAT["i"])


ani = None

if __name__ == "__main__":
    if os.environ.get("DISPLAY") or os.environ.get("ALLOW_GUI"):
        ani = FuncAnimation(
            fig, update, frames=len(ts), interval=1000 / FPS,
            blit=False, repeat=True,
        )
        plt.show()
    else:
        # Mode headless : GIF sans gestion de pause (bouton non interactif)
        def save_update(frame):
            dessine(frame)

        ani = FuncAnimation(
            fig, save_update, frames=len(ts),
            interval=1000 / FPS, blit=False, repeat=False,
        )
        ani.save("photo_video.gif", writer=PillowWriter(fps=FPS))
        print("Animation écrite dans photo_video.gif")
