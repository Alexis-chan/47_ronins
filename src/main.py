"""main.py
Point d’entrée du jeu : initialisation de Pygame, création de la fenêtre, boucle principale.
La scène est dessinée sur une surface 320×240 puis mise à l’échelle x3 → 960×720
pour un rendu pixel‑perfect sans flou.
"""

from __future__ import annotations

import sys
from pathlib import Path
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
    FULLSCREEN,
)
from player import Player


def main() -> None:
    """Lance le jeu."""

    # Initialisation
    pygame.init()
    pygame.display.set_caption("47 Ronins Chats – Prototype")

   # Fenêtre et surface de rendu pixelisée
    flags = pygame.FULLSCREEN if FULLSCREEN else 0
    window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), flags)
    canvas = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)).convert()
    clock = pygame.time.Clock()


    # Chemins absolus des assets
    music_path = Path(MUSIC_FILE)
    background_path = Path(BACKGROUND_IMG)

    # Chargement audio + image
    pygame.mixer.music.load(str(music_path))
    pygame.mixer.music.play(-1)

    background = pygame.image.load(str(background_path)).convert()
    background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))

 
    # Entités
    player = Player((WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20))
    platform = pygame.Rect(WINDOW_WIDTH // 4, WINDOW_HEIGHT - 60, 80, 10)

    # Petit sprite pour les coeurs
    heart = pygame.Surface((12, 10), pygame.SRCALPHA)
    pygame.draw.circle(heart, (255, 0, 0), (3, 3), 3)
    pygame.draw.circle(heart, (255, 0, 0), (9, 3), 3)
    pygame.draw.polygon(heart, (255, 0, 0), [(0, 5), (12, 5), (6, 9)])

    # Boucle principale
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                player.start_attack()

        pressed = pygame.key.get_pressed()
        player.update(pressed, [platform])

        canvas.blit(background, (0, 0))
        pygame.draw.rect(canvas, (139, 69, 19), platform)
        player.draw(canvas)
        player.draw_health(canvas, heart)

        pygame.transform.scale(canvas, (DISPLAY_WIDTH, DISPLAY_HEIGHT), window)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
