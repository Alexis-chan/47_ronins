"""main.py
Point d’entrée du jeu : initialisation de Pygame, création de la fenêtre, boucle principale.
La scène est dessinée sur une surface 320×240 puis mise à l’échelle x3 → 960×720
pour un rendu pixel‑perfect sans flou.
"""

from __future__ import annotations

import os
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

    # Initialisation
    pygame.init()
    pygame.display.set_caption("47 Ronins Chats – Prototype")

   # Fenêtre et surface de rendu pixelisée
    window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    canvas = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)).convert()
    clock = pygame.time.Clock()


    # Gestion des chemins
    script_dir = os.path.dirname(__file__)
    music_path = os.path.join(script_dir, r"../assets/son/Music1.wav")
    background_path = os.path.join(script_dir, BACKGROUND_IMG)

    # Chargement audio + image
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)

    background = pygame.image.load(background_path).convert()

 
    # Entités
    player = Player((WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20))

    # Boucle principale
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pressed = pygame.key.get_pressed()
        player.update(pressed)

        canvas.blit(background, (0, 0))
        player.draw(canvas)

        pygame.transform.scale(canvas, (DISPLAY_WIDTH, DISPLAY_HEIGHT), window)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
