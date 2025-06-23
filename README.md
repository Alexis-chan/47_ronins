# 47_ronins
Jeu sidescroller 47_ronin

## Configuration

Les paramètres du jeu sont définis dans [`src/settings.py`](src/settings.py).
La résolution est à présent de 1280×960 (320×240 mis à l'échelle ×4).
Le jeu démarre en mode fenêtré par défaut (`FULLSCREEN = False`).

## Visualiser le prototype du premier stage

Un script facultatif (`src/stage1_blueprint.py`) permet de charger l'image de
référence `model_stage_1.png` (dossier `Exemple`) et d'afficher par dessus les
plates-formes, l'échelle et les emplacements approximatifs des ennemis.

```bash
python3 src/stage1_blueprint.py
```

La fenêtre ainsi ouverte reproduit la disposition générale décrite dans les
spécifications du stage.
