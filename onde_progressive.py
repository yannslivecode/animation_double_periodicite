#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Double périodicité d'une onde progressive sinusoïdale (Terminale)
================================================================

Onde étudiée :  y(x, t) = A · cos[ 2π ( t/T − x/λ ) ]   (propagation vers +x)

Codage pédagogique (constant sur toute l'animation)
  • BLEU   = ESPACE : la longueur d'onde λ (distance entre deux crêtes voisines
             sur la « photo » de la corde à t fixé).
  • ORANGE = TEMPS  : la période T (durée entre deux maxima successifs en un
             point M fixé, sur le graphe y(t) du bas).
  • VERT   = VITESSE : une crête suivie au cours du temps ; en une période T
             elle avance exactement de λ  ⇒  v = λ / T.

Utilisation
  • Lancer :  python onde_progressive.py
  • Le GIF est d'abord exporté (désactivable : EXPORTER_GIF = False),
    puis la fenêtre interactive s'ouvre EN PLEIN ÉCRAN (ou maximisée).
  • Contrôles : boutons de lecture/pause et menu à gauche.
  • Menu :
    - Pause/Reprise : espace ou bouton ▶/⏸
    - Afficher/cacher les informations : cases à cocher
    - Choisir un milieu de propagation : boutons radio
  • En pause : flèches ← / → pour avancer/reculer image par image.
  • Touche « f » : basculer le plein écran (utile pour la projection).

Dépendances : numpy, matplotlib (Pillow pour l'export GIF).
"""

import itertools
import os

import matplotlib

# La fenêtre interactive exige un backend GUI (TkAgg, QtAgg, macOS, Windows).
# Si aucun n'est disponible (serveur sans affichage, Python sans Tk), on reste
# sur le backend par défaut (souvent Agg) : le GIF est quand même exporté et
# un message clair est affiché à la place de la fenêtre.
def _backend_graphique_disponible():
    try:
        import tkinter  # noqa: F401
        return True
    except Exception:
        pass
    for mod in ("PyQt6", "PySide6", "PyQt5", "PySide2", "wx"):
        try:
            __import__(mod)
            return True
        except Exception:
            continue
    backend = matplotlib.get_backend().lower()
    return backend not in ("agg", "pdf", "ps", "svg", "cairo")

if _backend_graphique_disponible() and matplotlib.get_backend().lower() == "agg":
    for _candidat in ("TkAgg", "QtAgg", "Qt5Agg"):
        try:
            matplotlib.use(_candidat, force=True)
            break
        except Exception:
            continue

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyArrowPatch
from matplotlib.widgets import Button, CheckButtons, RadioButtons

# ============================================================================
# 1) PARAMÈTRES MODIFIABLES PAR LE PROFESSEUR
# ============================================================================
# On choisit A, λ et T ; la célérité v = λ/T est CALCULÉE (jamais saisie) :
# les trois grandeurs restent donc toujours cohérentes entre elles.
#
#   Exemples réalistes (corde / cuve à ondes) :
#     A = 2.0 cm ; λ = 0.40 m ; T = 0.50 s  ->  v = 0.80 m/s   (par défaut)
#     A = 1.5 cm ; λ = 0.60 m ; T = 0.30 s  ->  v = 2.00 m/s
#     A = 2.5 cm ; λ = 0.30 m ; T = 0.75 s  ->  v = 0.40 m/s

# Prédéfinis de milieux de propagation
# Format : {"nom": (A_cm, lambda_m, T_s)}
MILIEUX = {
    "Corde tendue (v ≈ 0,8 m/s)": (2.0, 0.40, 0.50),
    "Eau peu profonde (v ≈ 0,4 m/s)": (1.8, 0.30, 0.75),
    "Eau profonde (v ≈ 1,2 m/s)": (2.0, 0.48, 0.40),
    "Ressort (v ≈ 0,6 m/s)": (2.2, 0.36, 0.60),
}

MILIEU_DEFAUT = "Corde tendue (v ≈ 0,8 m/s)"
A_CM, LAMBDA, T = MILIEUX[MILIEU_DEFAUT]

X_OBS = 0.5 * LAMBDA   # position du point M observé (graphe y(t)) ; de
                       # préférence entre 0 et λ pour ne pas gêner les flèches

# --- Réglages de l'animation ------------------------------------------------
NB_PERIODES = 3          # durée affichée sur le graphe y(t) et durée du GIF
IMAGES_PAR_PERIODE = 24  # fluidité (nombre d'images pour une période T)
INTERVALLE_MS = 50       # durée d'affichage d'une image (ms) -> ralenti
EXPORTER_GIF = True
NOM_GIF = "onde_progressive.gif"
DPI_GIF = 72             # résolution du GIF (plus grand = plus lourd)

# --- Adaptation à l'écran ---------------------------------------------------
MAXIMISER_AU_DEMARRAGE = True  # la fenêtre interactive occupe tout l'écran
LARGEUR_MIN, HAUTEUR_MIN = 10.0, 6.5   # taille de repli (pouces) si la
                                       # maximisation échoue

# ============================================================================
# 2) VÉRIFICATIONS ET GRANDEURS DÉRIVÉES
# ============================================================================
assert A_CM > 0 and LAMBDA > 0 and T > 0, "A, λ et T doivent être > 0"
assert isinstance(NB_PERIODES, int) and NB_PERIODES >= 2, "NB_PERIODES entier >= 2"
assert 0 <= X_OBS <= 3 * LAMBDA - 1e-9, "X_OBS doit être dans [0 ; 3λ]"

V = LAMBDA / T                       # célérité v = λ/T  (m/s)
DT = T / IMAGES_PAR_PERIODE          # pas de temps simulé entre 2 images
FENETRE = NB_PERIODES * T            # durée totale du graphe y(t)
N_LAMBDA_VISIBLES = 3                # nombre de longueurs d'onde affichées

# Couleurs (contrastées, lisibles en projection)
C_ESPACE = "#1f5fbf"   # bleu
C_TEMPS = "#e07000"    # orange
C_VITESSE = "#178a34"  # vert
C_ONDE = "#1a1a1a"     # noir

# Polices dimensionnées pour la projection
plt.rcParams.update({
    "font.size": 17,
    "axes.labelsize": 19,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "axes.titlesize": 20,
})


def fr(valeur, nd=2):
    """Formate un nombre avec la virgule décimale française."""
    return f"{valeur:.{nd}f}".replace(".", ",")


def fr_math(valeur, nd=2):
    """Idem pour du texte mathématique (virgule sans espace parasite)."""
    return f"{valeur:.{nd}f}".replace(".", "{,}")


def adapter_a_l_ecran(fig):
    """Agrandit la fenêtre de la figure au maximum, quel que soit le backend.

    Essaie successivement les API des principaux backends interactifs :
    Qt (PyQt/PySide), TkAgg, wxAgg, puis le plein écran générique de
    matplotlib. Ne fait rien en cas d'échec (la fenêtre garde sa taille).
    """
    mgr = fig.canvas.manager
    # 1) Qt : showMaximized() respecte la barre des tâches
    try:
        mgr.window.showMaximized()
        return
    except (AttributeError, Exception):
        pass
    # 2) TkAgg (Windows/Linux) : fenêtre zoomée
    try:
        mgr.window.state("zoom")
        return
    except Exception:
        pass
    # 3) wxAgg
    try:
        mgr.frame.Maximize(True)
        return
    except Exception:
        pass
    # 4) Repli générique : plein écran matplotlib (macOS, etc.)
    try:
        mgr.full_screen_toggle()
    except Exception:
        pass


def taille_ecran_pouces():
    """Renvoie (largeur, hauteur) de l'écran en pouces, ou None si inconnu.

    Sert à dimensionner la figure pour qu'elle remplisse l'écran sur les
    backends où la maximisation de fenêtre échoue.
    """
    try:
        import tkinter
        racine = tkinter.Tk()
        racine.update_idletasks()
        dpi_ecran = racine.winfo_fpixels("1i") or 96.0
        w = racine.winfo_screenwidth() / dpi_ecran
        h = racine.winfo_screenheight() / dpi_ecran
        racine.destroy()
        return max(w, 1.0), max(h, 1.0)
    except Exception:
        return None


# ============================================================================
# 3) CONSTRUCTION DE LA FIGURE
# ============================================================================
def construire_figure(dpi, A_param, lambda_param, T_param, x_obs_param):
    """Crée la figure et renvoie (fig, dessiner, label_pause, etat_ui).

    dessiner(t) redessine l'image correspondant à l'instant simulé t (s).
    etat_ui contient les références aux éléments d'interface pour afficher/cacher.

    La figure est créée à la taille de l'écran si celui-ci est détecté
    (fenêtre interactive) ; pour l'export GIF, passer dpi=DPI_GIF et un
    figsize fixé par l'appelant.
    """
    A = A_param
    lam = lambda_param
    T_p = T_param
    x_obs = x_obs_param
    V = lam / T_p

    # Taille de la fenêtre : plein écran si possible, repli sinon
    if dpi == DPI_GIF:
        figsize = (17, 9.5)          # taille fixe pour le GIF
    else:
        taille = taille_ecran_pouces()
        if taille is not None:
            # on laisse ~96 % de l'écran pour ne pas masquer les bords
            figsize = (0.96 * taille[0], 0.90 * taille[1])
        else:
            figsize = (LARGEUR_MIN, HAUTEUR_MIN)

    fig = plt.figure(figsize=figsize, dpi=dpi)
    gs = GridSpec(2, 2, figure=fig, width_ratios=[3, 1.2],
                  height_ratios=[1.15, 1], left=0.065, right=0.985,
                  top=0.94, bottom=0.13, wspace=0.07, hspace=0.62)
    ax_x = fig.add_subplot(gs[0, 0])
    ax_t = fig.add_subplot(gs[1, 0])
    ax_i = fig.add_subplot(gs[:, 1])

    # ------------------------------------------------------------------
    # Graphe du haut : « photo » y(x) à t fixé  -> périodicité spatiale
    # ------------------------------------------------------------------
    x = np.linspace(0, N_LAMBDA_VISIBLES * lam, 900)
    ax_x.set_xlim(-0.05 * lam, (N_LAMBDA_VISIBLES + 0.05) * lam)
    ax_x.set_ylim(-2.2 * A, 2.2 * A)
    ax_x.set_title("Photo à t fixé : y(x)  —  périodicité dans l'ESPACE (λ)",
                   color=C_ESPACE, fontweight="bold", pad=10)
    ax_x.set_xlabel("x (m)")
    ax_x.set_ylabel("y (cm)")
    ax_x.set_xticks([n * lam for n in range(N_LAMBDA_VISIBLES + 1)])
    ax_x.set_xticklabels(["0"] + [f"{n}λ\n{fr(n * lam)} m"
                                  for n in range(1, N_LAMBDA_VISIBLES + 1)])
    ax_x.set_yticks([-A, 0, A])
    ax_x.set_yticklabels(["−A", "0", "A"])
    ax_x.grid(alpha=0.25)
    ax_x.axhline(0, color="gray", lw=1.5)

    y_fleche_l = 1.4 * A      # hauteur de la flèche λ
    y_fleche_d = -1.4 * A     # hauteur de la flèche d = v·τ

    onde, = ax_x.plot([], [], color=C_ONDE, lw=4.5, zorder=3)

    # Point M fixe (orange) : il monte et descend -> lien avec y(t)
    ax_x.plot([x_obs, x_obs], [-1.2 * A, 1.3 * A], color=C_TEMPS, ls=":", lw=3)
    ax_x.text(x_obs, 1.42 * A, "point M", color=C_TEMPS, fontsize=19,
              fontweight="bold", ha="center", va="bottom")
    pt_M, = ax_x.plot([], [], "o", color=C_TEMPS, ms=20, mec="white",
                      mew=2.5, zorder=5)

    # Crête suivie (vert) + flèche λ (bleu) entre deux crêtes voisines
    crete, = ax_x.plot([], [], "D", color=C_VITESSE, ms=17, mec="white",
                       mew=2, zorder=6)
    vl1, = ax_x.plot([], [], color=C_ESPACE, ls="--", lw=2.5)
    vl2, = ax_x.plot([], [], color=C_ESPACE, ls="--", lw=2.5)
    fl_lambda = FancyArrowPatch((0, 0), (1, 1), arrowstyle="<|-|>",
                                mutation_scale=38, lw=4.5, color=C_ESPACE,
                                shrinkA=0, shrinkB=0, zorder=4)
    ax_x.add_patch(fl_lambda)
    txt_lambda = ax_x.text(0, y_fleche_l + 0.1 * A, "λ", color=C_ESPACE,
                           fontsize=32, fontweight="bold", ha="center",
                           va="bottom")

    # Départ de la crête suivie (repère fixe) et distance parcourue d
    ax_x.plot([lam, lam], [y_fleche_d, A], color=C_VITESSE, ls=":",
              lw=2.5, alpha=0.8)
    ax_x.text(lam - 0.02 * lam, y_fleche_d, "départ", color=C_VITESSE,
              fontsize=17, ha="right", va="center")
    vl_c, = ax_x.plot([], [], color=C_VITESSE, ls=":", lw=2.5, alpha=0.8)
    fl_d = FancyArrowPatch((0, 0), (1, 1), arrowstyle="-|>",
                           mutation_scale=38, lw=4.5, color=C_VITESSE,
                           shrinkA=0, shrinkB=0, zorder=4)
    ax_x.add_patch(fl_d)
    txt_d = ax_x.text(0, y_fleche_d - 0.12 * A, "d = v·τ", color=C_VITESSE,
                      fontsize=24, fontweight="bold", ha="center", va="top")

    # ------------------------------------------------------------------
    # Graphe du bas : y(t) au point M  -> périodicité temporelle
    # ------------------------------------------------------------------
    t_grille = np.linspace(0, NB_PERIODES * T_p, 800)
    y_t = A * np.cos(2 * np.pi * (t_grille / T_p - x_obs / lam))
    ax_t.set_xlim(0, NB_PERIODES * T_p)
    ax_t.set_ylim(-2.2 * A, 2.2 * A)
    ax_t.set_title(f"Film au point M fixe (x = {fr(x_obs)} m) : y(t)  —  "
                   "périodicité dans le TEMPS (T)",
                   color=C_TEMPS, fontweight="bold", pad=10)
    ax_t.set_xlabel("t (s)")
    ax_t.set_ylabel("y (cm)")
    ax_t.set_xticks([n * T_p for n in range(NB_PERIODES + 1)])
    ax_t.set_xticklabels(["0"] + [f"{n}T\n{fr(n * T_p)} s"
                                  for n in range(1, NB_PERIODES + 1)])
    ax_t.set_yticks([-A, 0, A])
    ax_t.set_yticklabels(["−A", "0", "A"])
    ax_t.grid(alpha=0.25)
    ax_t.axhline(0, color="gray", lw=1.5)
    ax_t.plot(t_grille, y_t, color=C_TEMPS, lw=3, alpha=0.25)  # courbe fantôme
    trace, = ax_t.plot([], [], color=C_TEMPS, lw=4.5, zorder=3)
    curseur, = ax_t.plot([], [], "o", color=C_TEMPS, ms=20, mec="white",
                         mew=2.5, zorder=5)

    # Flèche T entre les deux premiers maxima de y(t)
    t1 = T_p * ((x_obs / lam) % 1.0)
    if t1 < 1e-9:
        t1 = 0.0
    maxima = [t1 + k * T_p for k in range(NB_PERIODES) if t1 + k * T_p <= NB_PERIODES * T_p]
    ax_t.plot(maxima, [A] * len(maxima), "o", mfc="white", mec=C_TEMPS,
              mew=3, ms=13, zorder=4)
    yT = 1.4 * A
    for tm in maxima[:2]:
        ax_t.plot([tm, tm], [A, yT], color=C_TEMPS, ls="--", lw=2.5)
    if len(maxima) >= 2:
        ax_t.add_patch(FancyArrowPatch((maxima[0], yT), (maxima[1], yT),
                                       arrowstyle="<|-|>", mutation_scale=38,
                                       lw=4.5, color=C_TEMPS, shrinkA=0,
                                       shrinkB=0, zorder=4))
        ax_t.text((maxima[0] + maxima[1]) / 2, yT + 0.1 * A, "T", color=C_TEMPS,
                  fontsize=32, fontweight="bold", ha="center", va="bottom")

    # ------------------------------------------------------------------
    # Panneau d'information à droite
    # ------------------------------------------------------------------
    ax_i.set_xlim(0, 1)
    ax_i.set_ylim(0, 1)
    ax_i.set_xticks([])
    ax_i.set_yticks([])
    for s in ax_i.spines.values():
        s.set_color("#999999")
        s.set_linewidth(1.5)

    def texte(px, py, s, **kw):
        kw.setdefault("va", "top")
        return ax_i.text(px, py, s, transform=ax_i.transAxes, **kw)

    txt_titre = texte(0.05, 0.975, "Équation de l'onde", fontsize=19, fontweight="bold")
    txt_eq1 = texte(0.05, 0.925,
          r"$y(x,t)=A\,\cos\!\left[2\pi\left(\frac{t}{T}-\frac{x}{\lambda}"
          r"\right)\right]$", fontsize=21)
    txt_eq2 = texte(0.05, 0.815,
          "$y=" + fr_math(A, 1) + r"\,\cos[2\pi(t/" + fr_math(T_p)
          + "-x/" + fr_math(lam) + ")]$", fontsize=16)
    txt_eq3 = texte(0.05, 0.77, "(y en cm, x en m, t en s)", fontsize=13, color="gray")

    txt_lambda_titre = texte(0.05, 0.705, f"λ = {fr(lam)} m", fontsize=25, fontweight="bold",
          color=C_ESPACE)
    txt_lambda_desc = texte(0.05, 0.655, "distance entre 2 crêtes\nvoisines, à t fixé",
          fontsize=15, color=C_ESPACE)

    txt_t_titre = texte(0.05, 0.555, f"T = {fr(T_p)} s", fontsize=25, fontweight="bold",
          color=C_TEMPS)
    txt_t_desc = texte(0.05, 0.505, "durée entre 2 maxima\nen un point fixe",
          fontsize=15, color=C_TEMPS)

    txt_v_titre = texte(0.05, 0.405, "v = λ / T", fontsize=25, fontweight="bold",
          color=C_VITESSE)
    txt_v_calc = texte(0.05, 0.355, f"= {fr(lam)} / {fr(T_p)} = {fr(V)} m/s",
          fontsize=19, fontweight="bold", color=C_VITESSE)
    txt_v_desc = texte(0.05, 0.305, "En une période T, la crête\navance de λ.",
          fontsize=15, color=C_VITESSE)

    ax_i.plot([0.04, 0.96], [0.215, 0.215], color="#999999", lw=1.5,
              transform=ax_i.transAxes)
    txt_t = texte(0.05, 0.195, "", fontsize=19, fontweight="bold")
    txt_tau = texte(0.05, 0.13, "", fontsize=19, color="#333333")
    txt_dist = texte(0.05, 0.065, "", fontsize=19, fontweight="bold",
                     color=C_VITESSE)

    label_pause = fig.text(0.985, 0.975, "", color="#c00000", fontsize=26,
                           fontweight="bold", ha="right", va="top")

    # Grouper les éléments d'info pour afficher/cacher
    etat_ui = {
        "ax_i": ax_i,
        "info_elements": [txt_titre, txt_eq1, txt_eq2, txt_eq3,
                          txt_lambda_titre, txt_lambda_desc,
                          txt_t_titre, txt_t_desc,
                          txt_v_titre, txt_v_calc, txt_v_desc],
        "dynamic_elements": [txt_t, txt_tau, txt_dist],
    }

    # ------------------------------------------------------------------
    # Mise à jour d'une image
    # ------------------------------------------------------------------
    def dessiner(t):
        tau = t % T_p                       # temps écoulé dans la période en cours
        # Photo de l'onde à l'instant t
        y = A * np.cos(2 * np.pi * (t / T_p - x / lam))
        onde.set_data(x, y)

        # Point M
        yM = A * np.cos(2 * np.pi * (t / T_p - x_obs / lam))
        pt_M.set_data([x_obs], [yM])

        # Crête suivie : à τ = 0 elle est en x = λ ; elle avance de v·τ
        d = V * tau
        xc = lam + d
        crete.set_data([xc], [A])
        vl1.set_data([xc, xc], [A, y_fleche_l])
        vl2.set_data([xc + lam, xc + lam], [A, y_fleche_l])
        fl_lambda.set_positions((xc, y_fleche_l), (xc + lam, y_fleche_l))
        txt_lambda.set_position((xc + lam / 2, y_fleche_l + 0.1 * A))

        vl_c.set_data([xc, xc], [A, y_fleche_d])
        visible = d > 1e-6 * lam
        fl_d.set_visible(visible)
        txt_d.set_visible(visible)
        if visible:
            fl_d.set_positions((lam, y_fleche_d), (xc, y_fleche_d))
            txt_d.set_position((lam + d / 2, y_fleche_d - 0.12 * A))
            txt_d.set_text("d = v·τ" if d > 0.35 * lam else "d")

        # Graphe y(t) : trace jusqu'à l'instant courant (fenêtre glissante
        # remise à zéro toutes les NB_PERIODES périodes)
        tw = t % (NB_PERIODES * T_p)
        masque = t_grille <= tw
        trace.set_data(t_grille[masque], y_t[masque])
        curseur.set_data([tw], [A * np.cos(2 * np.pi * (tw / T_p - x_obs / lam))])

        # Panneau d'information dynamique
        txt_t.set_text(f"t = {fr(t)} s")
        txt_tau.set_text(f"τ = {fr(tau)} s   (T = {fr(T_p)} s)")
        txt_dist.set_text(f"d = v·τ = {fr(d)} m")

    return fig, dessiner, label_pause, etat_ui


# ============================================================================
# 4) EXPORT GIF
# ============================================================================
def exporter_gif():
    """Enregistre un GIF de NB_PERIODES périodes (bouclage parfait)."""
    fig, dessiner, _, _ = construire_figure(DPI_GIF, A_CM, LAMBDA, T, X_OBS)
    n_images = NB_PERIODES * IMAGES_PAR_PERIODE
    ani = FuncAnimation(fig, lambda i: dessiner(i * DT), frames=n_images,
                        interval=INTERVALLE_MS, repeat=True)
    chemin = os.path.join(os.path.dirname(os.path.abspath(__file__)), NOM_GIF)
    print(f"Export du GIF en cours ({n_images} images) : {chemin}")
    ani.save(chemin, writer=PillowWriter(fps=1000 / INTERVALLE_MS))
    plt.close(fig)
    print(f"GIF enregistré : {chemin}")


# ============================================================================
# 5) ANIMATION INTERACTIVE (boutons de contrôle, menus)
# ============================================================================
def animation_interactive():
    # Libère les flèches et 'f' de leurs raccourcis par défaut de matplotlib
    plt.rcParams["keymap.back"] = []
    plt.rcParams["keymap.forward"] = []
    plt.rcParams["keymap.quit"] = ["ctrl+w", "cmd+w"]
    # 'f' reste dans keymap.fullscreen -> bascule plein écran gérée par
    # matplotlib ; on garde aussi un repli manuel ci-dessous.

    # État global (utiliser un conteneur pour éviter les problèmes de nonlocal)
    ctx = {"fig": None, "dessiner": None, "label_pause": None, "ui_refs": None,
           "ani": None, "t": 0.0, "pause": False, "milieu": MILIEU_DEFAUT,
           "afficher_info": True, "A": A_CM, "lambda": LAMBDA, "T": T,
           "x_obs": X_OBS}

    # ---- Fonctions de contrôle
    def basculer_pause():
        """Basculer pause/lecture."""
        ctx["pause"] = not ctx["pause"]
        ctx["label_pause"].set_text("PAUSE" if ctx["pause"] else "")
        ctx["fig"].canvas.draw_idle()

    def demarrer_lecture():
        """Reprendre la lecture."""
        ctx["pause"] = False
        ctx["label_pause"].set_text("")
        ctx["fig"].canvas.draw_idle()

    def image_precedente():
        """Aller à l'image précédente (en pause)."""
        if ctx["pause"]:
            ctx["t"] = max(0.0, ctx["t"] - DT)
            ctx["dessiner"](ctx["t"])
            ctx["fig"].canvas.draw_idle()

    def image_suivante():
        """Aller à l'image suivante (en pause)."""
        if ctx["pause"]:
            ctx["t"] += DT
            ctx["dessiner"](ctx["t"])
            ctx["fig"].canvas.draw_idle()

    def basculer_affichage():
        """Afficher/masquer le panneau d'information."""
        ctx["afficher_info"] = not ctx["afficher_info"]
        afficher_masquer_infos()

    def afficher_masquer_infos():
        """Basculer la visibilité des infos."""
        vis = ctx["afficher_info"]
        for elem in ctx["ui_refs"]["info_elements"]:
            elem.set_visible(vis)
        ctx["ui_refs"]["ax_i"].spines["right"].set_visible(vis)
        ctx["ui_refs"]["ax_i"].spines["top"].set_visible(vis)
        ctx["ui_refs"]["ax_i"].spines["bottom"].set_visible(vis)
        ctx["ui_refs"]["ax_i"].spines["left"].set_visible(vis)
        ctx["fig"].canvas.draw_idle()

    def image(_):
        """Mise à jour pour chaque frame de l'animation."""
        if not ctx["pause"]:
            ctx["t"] += DT
        ctx["dessiner"](ctx["t"])

    def basculer_plein_ecran():
        """Basculer le plein écran (raccourci 'f' + repli manuel)."""
        try:
            ctx["fig"].canvas.manager.full_screen_toggle()
        except Exception:
            adapter_a_l_ecran(ctx["fig"])

    def touche_clavier(evt):
        """Gestion des touches clavier."""
        if evt.key == " ":
            basculer_pause()
        elif evt.key == "f":
            basculer_plein_ecran()
        elif ctx["pause"] and evt.key in ("right", "left"):
            ctx["t"] = max(0.0, ctx["t"] + (DT if evt.key == "right" else -DT))
            ctx["dessiner"](ctx["t"])
            ctx["fig"].canvas.draw_idle()

    def mettre_a_jour_milieu(label):
        """Rappel : changement de milieu."""
        a, lam, t = MILIEUX[label]
        ctx["milieu"] = label
        ctx["A"] = a
        ctx["lambda"] = lam
        ctx["T"] = t
        ctx["x_obs"] = 0.5 * lam
        ctx["t"] = 0.0
        ctx["pause"] = True
        # Fermer l'ancienne figure et en recréer une
        plt.close(ctx["fig"])
        construire_ui()

    def construire_ui():
        """Construire la figure et les contrôles."""
        # Construire la figure initiale (dimensionnée à l'écran)
        ctx["fig"], ctx["dessiner"], ctx["label_pause"], ctx["ui_refs"] = (
            construire_figure(100, ctx["A"], ctx["lambda"], ctx["T"], ctx["x_obs"]))

        # ---- Contrôles de lecture (bas à gauche)
        ax_pause_btn = ctx["fig"].add_axes([0.068, 0.032, 0.06, 0.05])
        btn_pause = Button(ax_pause_btn, "Pause", color="#e8e8e8",
                           hovercolor="#cfcfcf")
        btn_pause.label.set_fontsize(14)
        btn_pause.on_clicked(lambda _: basculer_pause())

        ax_play_btn = ctx["fig"].add_axes([0.135, 0.032, 0.06, 0.05])
        btn_play = Button(ax_play_btn, "Lire", color="#e8e8e8",
                          hovercolor="#cfcfcf")
        btn_play.label.set_fontsize(14)
        btn_play.on_clicked(lambda _: demarrer_lecture())

        ax_prev_btn = ctx["fig"].add_axes([0.202, 0.032, 0.06, 0.05])
        btn_prev = Button(ax_prev_btn, "< Prec", color="#e8e8e8",
                          hovercolor="#cfcfcf")
        btn_prev.label.set_fontsize(14)
        btn_prev.on_clicked(lambda _: image_precedente())

        ax_next_btn = ctx["fig"].add_axes([0.269, 0.032, 0.06, 0.05])
        btn_next = Button(ax_next_btn, "Suiv >", color="#e8e8e8",
                          hovercolor="#cfcfcf")
        btn_next.label.set_fontsize(14)
        btn_next.on_clicked(lambda _: image_suivante())

        # ---- Menu affichage/masquage des infos (bas)
        ax_check_info = ctx["fig"].add_axes([0.37, 0.028, 0.15, 0.06])
        check_info = CheckButtons(ax_check_info, ["Afficher infos"],
                                  [ctx["afficher_info"]])
        for label in check_info.labels:
            label.set_fontsize(14)
        check_info.on_clicked(lambda label: basculer_affichage())

        # ---- Menu choix du milieu (bas)
        ax_milieux = ctx["fig"].add_axes([0.545, 0.028, 0.17, 0.12])
        noms_milieux = list(MILIEUX.keys())
        radio_milieux = RadioButtons(ax_milieux, noms_milieux,
                                     active=noms_milieux.index(ctx["milieu"]))
        for label in radio_milieux.labels:
            label.set_fontsize(13)
        radio_milieux.on_clicked(mettre_a_jour_milieu)
        ax_milieux.text(-0.15, 1.05, "Milieu :", fontsize=14, fontweight="bold",
                        transform=ax_milieux.transAxes, ha="left", va="bottom")

        # ---- Aide (bas à droite)
        ctx["fig"].text(0.73, 0.05, "Espace : pause  |  f : plein écran",
                        fontsize=13, color="#555555", va="center")

        # ---- Animation
        ctx["fig"].canvas.mpl_connect("key_press_event", touche_clavier)
        ctx["dessiner"](ctx["t"])
        afficher_masquer_infos()

        ctx["ani"] = FuncAnimation(ctx["fig"], image, frames=itertools.count(),
                                   interval=INTERVALLE_MS, cache_frame_data=False)
        ctx["fig"]._ani = ctx["ani"]
        ctx["fig"]._controls = (btn_pause, btn_play, btn_prev, btn_next,
                                check_info, radio_milieux)

        # ---- Adapter la fenêtre à l'écran UNE fois la figure créée
        if MAXIMISER_AU_DEMARRAGE:
            adapter_a_l_ecran(ctx["fig"])

    if not _backend_graphique_disponible():
        print("Aucun backend graphique disponible (pas d'affichage ou Tk absent).")
        print("Le GIF a ete exporte ; pour la fenetre interactive, installez")
        print("par exemple :  pip install pyqt6")
        return

    # Construire la UI initiale et afficher
    construire_ui()
    plt.show()


if __name__ == "__main__":
    if EXPORTER_GIF:
        exporter_gif()
    animation_interactive()
