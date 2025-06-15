"""main.py
Point d’entrée du jeu : initialisation de Pygame, création de la fenêtre, boucle principale.
La scène est dessinée sur une surface 320×240 puis mise à l’échelle x3 → 960×720
pour un rendu pixel‑perfect sans flou.
"""

from __future__ import annotations

import sys
import pygame

from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
    SKY_BLUE,
    FPS,
    BACKGROUND_IMG,
    MUSIC_FILE,
)
from player import Player


def main() -> None:
    """Lance le jeu."""

    # —— Initialisation Pygame ——
    pygame.init()
    pygame.display.set_caption("47 Ronins Chats — Prototype")
    pygame.mixer.music.load(MUSIC_FILE)
    pygame.mixer.music.play(-1)

    # Surface affichée (agrandie) et surface interne (pixel‑art)
    window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    canvas = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)).convert()
    background = pygame.image.load(BACKGROUND_IMG).convert()
    background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))

    clock = pygame.time.Clock()

    # —— Entités ——
    player = Player((WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20))

    # —— Boucle principale ——
    running = True
    while running:
        # — Gestion des événements —
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pressed = pygame.key.get_pressed()

        # — Mise à jour du monde —
        player.update(pressed)

        # — Rendu sur la surface interne —
        canvas.blit(background, (0, 0))
        player.draw(canvas)

        # — Upscale + affichage —
        pygame.transform.scale(canvas, (DISPLAY_WIDTH, DISPLAY_HEIGHT), window)
        pygame.display.flip()

        # — Limitation FPS —
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
