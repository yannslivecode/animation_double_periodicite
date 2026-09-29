# Animation : double périodicité d'une onde sinusoïdale

Animation `matplotlib.animation` à deux panneaux synchronisés destinée à
illustrer en classe la différence entre **période spatiale** (longueur
d'onde λ) et **période temporelle** (période T).

## Analogie « photo / vidéo »

- **Panneau gauche** : la *photographie* de toute la corde à un instant t.
  C'est la fonction `y(x)` : on voit la période spatiale **λ**, distance
  entre deux crêtes (flèche verte).
- **Panneau droite** : la *vidéo* d'un seul point M de la corde.
  C'est la fonction `y_M(t)` qui se trace en temps réel : on voit la
  période temporelle **T**, durée d'une oscillation complète (flèche
  violette).

L'onde modélisée est une onde progressive sinusoïdale :

`y(x, t) = A · cos(2π (t/T − x/λ))`

Le point M (coloré) est suivi simultanément sur les deux panneaux.

## Paramètres

Modifiables en tête de `double_periodicite.py` :

| Paramètre | Rôle | Valeur par défaut |
|---|---|---|
| `A` | amplitude (m) | 1,0 |
| `T` | période temporelle (s) | 2,0 |
| `LAMBDA` | période spatiale λ (m) | 4,0 |
| `X_M` | abscisse du point M (m) | 5,0 |
| `DURATION` | durée de l'animation (s) | 2T |
| `FPS` | images par seconde | 30 |

## Utilisation

```bash
pip install matplotlib numpy pillow
python double_periodicite.py
```

Le script produit `double_periodicite.gif` (2 périodes temporelles, 3
longueurs d'onde visibles), directement projetable en classe.
