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

## Trois supports complémentaires

| Script | Objectif didactique | Sortie |
|---|---|---|
| `double_periodicite.py` | Version simple : introduction de la double périodicité | `double_periodicite.gif` |
| `photo_video_didactique.py` | Version didactique (blocage « je lis λ sur s(t) ») : axe horizontal central, code couleur, routine affichée | `photo_video.gif` |
| `quiz_deux_lectures.py` | Mini-quiz « même courbe, deux lectures » : l'élève nomme l'axe avant de mesurer | `quiz_deux_lectures.png` (interactif avec bouton) |

## Version didactique : l'axe horizontal est l'objet central

Pour lever la confusion « je lis λ sur un graphe s(t) » :

- **code couleur constant** : vert = espace (`x`, λ, mètres), violet = temps
  (`t`, T, secondes), rouge = point M ;
- **axe horizontal encadré et coloré**, avec libellé explicite :
  « axe des DISTANCES → on mesure λ » / « axe des DURÉES → on mesure T » ;
- **flèches avec valeur et unité** : λ = 40 cm et T = 2,0 s — les deux
  grandeurs n'ont pas la même unité ;
- **routine de lecture affichée en permanence** :
  ① Je nomme l'axe horizontal — ② `x (m)` → λ ; `t (s)` → T —
  ③ Je mesure entre deux motifs identiques ;
- la flèche T n'apparaît qu'une fois que deux motifs ont été tracés
  (t ≥ t₂), pour que la mesure ait un sens visuel.

Paramètres modifiables en tête de `photo_video_didactique.py` :
`A` (cm), `LAM` (λ, m), `T` (s), `V = λ/T`, `L` (corde affichée),
`X_M` (position de M), `T_MAX` (durée), `FPS`.

## Mini-quiz « même courbe, deux lectures »

Deux graphes **strictement identiques** (deux motifs consécutifs séparés
de « 4 »), axe horizontal masqué. Consigne : « Quelle grandeur mesure-t-on
entre deux motifs identiques ? Nomme d'abord l'axe ! »

Le bouton **« Révéler l'axe horizontal »** montre que le même « 4 » vaut :
- `T = 4 ms` sur le graphe A, `s(t)` — vidéo d'un point ;
- `λ = 4 cm` sur le graphe B, `y(x)` — photo de la corde.

## Scénario d'utilisation en classe

| Étape | Support | Consigne à l'élève |
|---|---|---|
| 1. Conflit cognitif (2 min) | Quiz, avant de cliquer | « Quelle grandeur mesure-t-on entre deux crêtes ? » Laisser émettre des hypothèses : on ne peut pas savoir sans l'axe. |
| 2. Révélation (1 min) | Clic sur le bouton | Constat : allure identique mais T ≠ λ (unités et grandeurs différentes). |
| 3. Construction du sens (5 min) | Animation | Prédiction avant lecture : « Quand M a fait un aller-retour complet, de combien la crête s'est-elle déplacée ? » Réponse : de λ, d'où λ = v·T. |
| 4. Variation (3 min) | Modifier `T` puis `LAM` | Doubler T change la vidéo seule ; doubler λ change la photo seule. |
| 5. Ancrage | Exercices papier | Écrire la routine en tête de chaque exercice : « axe horizontal = … donc je mesure … ». |

## Points de vigilance

- **Formulation** : bannir « distance entre deux crêtes » pour un graphe
  `s(t)`. Dire « entre deux motifs identiques ».
- **Prédire avant de regarder** : une animation seulement regardée reste
  passive. Faire écrire une prédiction avant chaque lancement.
- **Transfert vers le papier** : terminer avec des graphes en noir et
  blanc, abscisse d'abord cachée, pour que la routine devienne un
  réflexe indépendant du code couleur.
- **Évaluation de la remédiation** : proposer le même mini-exercice
  (lire T ou λ sur un graphe non légendé) en pré-test et en post-test
  pour mesurer si la confusion recule.

## Utilisation

```bash
pip install matplotlib numpy pillow
python double_periodicite.py          # version simple → .gif
python photo_video_didactique.py     # version didactique → photo_video.gif
python quiz_deux_lectures.py          # quiz interactif (fenêtre) ou → .png
```

Les GIF/PNG produits sont directement projectables en classe.
