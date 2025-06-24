from __future__ import annotations

"""Prototype de stage basé sur ``model_stage_1.png``.

Ce script sert uniquement à visualiser rapidement le décor de référence.
Contrairement à la version précédente, il n'affiche plus les plateformes
ni les emplacements des ennemis ; seul le personnage est dessiné devant le
fond. Les dimensions sont exprimées en pixels sur une surface 1920×512.
"""

from dataclasses import dataclass
from pathlib import Path

import pygame


# --- Données ---------------------------------------------------------------

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 512

IMAGE_PATH = Path(__file__).resolve().parent.parent / "Exemple" / "model_stage_1.png"


@dataclass
class Hero:
    x: int
    y: int


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

        # héros
        pygame.draw.circle(screen, (250, 250, 250), (ISAMU.x, ISAMU.y), 16)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
