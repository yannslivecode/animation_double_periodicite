# -*- coding: utf-8 -*-
"""
Animation : double périodicité d'une onde sinusoïdale le long d'une corde.

Analogie « photo / vidéo » :
  - Panneau gauche  : la PHOTOGRAPHIE de toute la corde à un instant donné,
                      y(x) = A cos(2π (t/T - x/λ)), avec un point M coloré.
  - Panneau droite  : la VIDEO d'un seul point, la courbe y_M(t) qui se
                      trace en temps réel.

Périodes mises en évidence :
  - période spatiale  λ (lambda) : distance entre deux crêtes sur la photo ;
  - période temporelle T        : durée d'une oscillation complète de M.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

# ------------------------------------------------------------------
# Paramètres physiques
# ------------------------------------------------------------------
A = 1.0          # amplitude (m)
T = 2.0          # période temporelle (s)
LAMBDA = 4.0     # période spatiale / longueur d'onde (m)
X_MAX = 3 * LAMBDA   # longueur de corde visible : 3 longueurs d'onde
X_M = LAMBDA + 1.0   # abscisse du point M suivi par la vidéo
DURATION = 2 * T     # durée de l'animation : 2 périodes temporelles
FPS = 30

# Grilles
x = np.linspace(0.0, X_MAX, 600)
t_grid = np.linspace(0.0, DURATION, int(DURATION * FPS) + 1)


def y_wave(xv, tv):
    """Déplacement de la corde : onde progressive sinusoïdale."""
    return A * np.cos(2.0 * np.pi * (tv / T - xv / LAMBDA))


# ------------------------------------------------------------------
# Figure à deux panneaux synchronisés
# ------------------------------------------------------------------
fig, (ax_photo, ax_video) = plt.subplots(
    1, 2, figsize=(11, 4.5), constrained_layout=True
)
fig.suptitle("Double périodicité :  photo de la corde  |  vidéo du point M",
             fontsize=13)

# --- Panneau gauche : la PHOTO y(x) --------------------------------
ax_photo.set_xlim(0.0, X_MAX)
ax_photo.set_ylim(-1.3 * A, 1.3 * A)
ax_photo.set_xlabel("x (m)")
ax_photo.set_ylabel("y (m)")
ax_photo.set_title(f"Photo de la corde à l'instant t\nλ = {LAMBDA:.0f} m (période spatiale)")

photo_line, = ax_photo.plot([], [], "b-", lw=2)
m_point, = ax_photo.plot([], [], "o", color="crimson", ms=10, zorder=5)
m_trace, = ax_photo.plot([], [], "-", color="crimson", lw=3, alpha=0.4, zorder=4)

# Repères de la période spatiale λ (flèche entre deux crêtes successives)
x_arrow = np.array([LAMBDA, 2 * LAMBDA])
ax_photo.annotate(
    "", xy=(x_arrow[1], -1.15 * A), xytext=(x_arrow[0], -1.15 * A),
    arrowprops=dict(arrowstyle="<->", color="green", lw=2),
)
ax_photo.text(1.5 * LAMBDA, -1.30 * A, "λ", ha="center", va="top",
              color="green", fontsize=12, fontweight="bold")

# --- Panneau droite : la VIDEO y_M(t) ------------------------------
ax_video.set_xlim(0.0, DURATION)
ax_video.set_ylim(-1.3 * A, 1.3 * A)
ax_video.set_xlabel("t (s)")
ax_video.set_ylabel("y_M (m)")
ax_video.set_title(f"Vidéo du point M (x = {X_M:.1f} m)\nT = {T:.0f} s (période temporelle)")

video_line, = ax_video.plot([], [], "-", color="crimson", lw=2)
video_dot, = ax_video.plot([], [], "o", color="crimson", ms=8)
video_cursor, = ax_video.plot([], [], "k:", lw=0.8)

# Repères de la période temporelle T (flèche entre deux maxima)
ax_video.annotate(
    "", xy=(T, 1.15 * A), xytext=(0.0, 1.15 * A),
    arrowprops=dict(arrowstyle="<->", color="purple", lw=2),
)
ax_video.text(T / 2, 1.25 * A, "T", ha="center", va="bottom",
              color="purple", fontsize=12, fontweight="bold")

# Chronomètre commun
time_text = fig.text(0.5, 0.015, "", ha="center", fontsize=11)


def init():
    photo_line.set_data([], [])
    m_point.set_data([], [])
    m_trace.set_data([], [])
    video_line.set_data([], [])
    video_dot.set_data([], [])
    video_cursor.set_data([], [])
    time_text.set_text("")
    return (photo_line, m_point, m_trace, video_line, video_dot,
            video_cursor, time_text)


def update(frame):
    t = t_grid[frame]

    # Photo : la corde entière à l'instant t
    photo_line.set_data(x, y_wave(x, t))

    # Point M sur la corde
    y_m = y_wave(X_M, t)
    m_point.set_data([X_M], [y_m])
    m_trace.set_data([X_M, X_M], [-1.3 * A, 1.3 * A])

    # Vidéo : y_M(t) qui se trace en temps réel
    t_past = t_grid[: frame + 1]
    y_past = y_wave(X_M, t_past)
    video_line.set_data(t_past, y_past)
    video_dot.set_data([t], [y_m])
    video_cursor.set_data([t, t], [-1.3 * A, 1.3 * A])

    time_text.set_text(f"t = {t:.2f} s")
    return (photo_line, m_point, m_trace, video_line, video_dot,
            video_cursor, time_text)


anim = FuncAnimation(
    fig, update, frames=len(t_grid), init_func=init, blit=False, interval=1000 / FPS
)

if __name__ == "__main__":
    anim.save("double_periodicite.gif", writer=PillowWriter(fps=FPS))
    print("Animation écrite dans double_periodicite.gif")
