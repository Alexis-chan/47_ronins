# 47_ronins
Jeu sidescroller 47_ronin

## Configuration

Les paramètres du jeu sont définis dans [`src/settings.py`](src/settings.py).
La résolution est à présent de 1280×960 (320×240 mis à l'échelle ×4).
Le jeu démarre en mode fenêtré par défaut (`FULLSCREEN = False`).

## Visualiser le prototype du premier stage

Le script optionnel [`src/stage1_blueprint.py`](src/stage1_blueprint.py) affiche
seulement l'arrière-plan principal ainsi qu'un repère pour le héros afin de
tester la résolution du jeu. Aucun élément de décor ou ennemi n'est chargé ;
c'est une base vierge pour préparer le niveau.

```bash
python3 src/stage1_blueprint.py
```
