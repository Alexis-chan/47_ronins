from __future__ import annotations

"""Prototype de stage basé sur `model_stage_1.png`.

Ce script n'est pas intégré au moteur du jeu existant.  Il sert uniquement
à visualiser la disposition approximative des plateformes et ennemis décrite
dans `Exemple/model_stage_1.png`.  Les dimensions sont exprimées en pixels
sur une surface 1920×512.
"""

from dataclasses import dataclass
from pathlib import Path

import pygame


# --- Données ---------------------------------------------------------------

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 512

IMAGE_PATH = Path(__file__).resolve().parent.parent / "Exemple" / "model_stage_1.png"


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


# Plateformes
PLATFORMS = [
    Platform(160, 384, 128, 32),  # Plateforme gauche basse
    Platform(480, 320, 128, 32),  # Plateforme centrale torii
    Platform(640, 256, 128, 32),  # Plateforme connectee a l'escalier
    # Escalier approximatif represente par petites marches
    Platform(448, 416, 192, 32),  # zone de marche de l'escalier (approx.)
    Platform(1344, 256, 320, 32),  # grande plateforme droite
]

# Echelle
LADDER = Platform(1664, 288, 32, 160)

# Ennemis
ENEMIES = [
    Enemy(64, 416),
    Enemy(176, 352),
    Enemy(496, 288),
    Enemy(576, 352),
    Enemy(656, 224),
    Enemy(1056, 64),
    Enemy(1472, 224),
]

# Héros
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

        # echelle
        pygame.draw.rect(screen, (180, 160, 120), LADDER.rect())

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
