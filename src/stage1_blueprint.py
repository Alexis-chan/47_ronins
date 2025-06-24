from __future__ import annotations

"""Prototype de stage basé sur `model_stage_1.png`.

Ce script n'est pas intégré au moteur du jeu existant.  Il sert uniquement
à visualiser la disposition approximative des plateformes et ennemis décrite
dans `Exemple/model_stage_1.png`.  Les dimensions sont exprimées en pixels
sur une surface 1920×512.
"""

from dataclasses import dataclass
from pathlib import Path
import json

import pygame


# --- Données ---------------------------------------------------------------

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 512

IMAGE_PATH = Path(__file__).resolve().parent.parent / "Exemple" / "model_stage_1.png"
LEVEL_FILE = Path(__file__).resolve().parent.parent / "levels" / "level1.json"


@dataclass
class Platform:
    x: int
    y: int
    width: int
    height: int

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)


@dataclass
class Enemy:
    x: int
    y: int


@dataclass
class Hero:
    x: int
    y: int


# Les donnees du niveau (plateformes et ennemis) sont lues depuis un fichier
# JSON pour faciliter les ajustements en fonction de l'image de reference.
def load_level(path: Path) -> tuple[list[Platform], list[Enemy]]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    plats = [
        Platform(p["x"], p["y"], p["width"], p["height"])
        for p in data.get("platforms", [])
    ]
    enemies = [Enemy(e["x"], e["y"]) for e in data.get("enemies", [])]
    return plats, enemies


PLATFORMS, ENEMIES = load_level(LEVEL_FILE)

# Position du heros d'apres l'image
ISAMU = Hero(1728, 224)


# --- Affichage ------------------------------------------------------------

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # fond
    try:
        background = pygame.image.load(str(IMAGE_PATH)).convert()
    except pygame.error:
        # Fallback : fond uni si l'image est introuvable
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background.fill((0, 100, 0))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(background, (0, 0))

        # plateformes
        for plat in PLATFORMS:
            pygame.draw.rect(screen, (139, 69, 19), plat.rect())

        # echelle (non utilisee dans ce prototype si non definie dans le JSON)

        # ennemis
        for en in ENEMIES:
            pygame.draw.circle(screen, (200, 0, 0), (en.x, en.y), 16)

        # héros
        pygame.draw.circle(screen, (250, 250, 250), (ISAMU.x, ISAMU.y), 16)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
