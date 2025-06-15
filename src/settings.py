"""settings.py
Définit toutes les constantes de configuration du jeu : dimensions d’écran, couleurs, physique, etc.
Ce fichier centralise les paramètres pour simplifier les ajustements ultérieurs.
"""

import pygame

# —— Dimensions d’origine (pixel‑art) ——
WINDOW_WIDTH: int = 320
WINDOW_HEIGHT: int = 240
UPSCALE: int = 3  # Facteur de mise à l’échelle (320×240 → 960×720)

DISPLAY_WIDTH: int = WINDOW_WIDTH * UPSCALE
DISPLAY_HEIGHT: int = WINDOW_HEIGHT * UPSCALE

# —— Couleurs ——
SKY_BLUE: tuple[int, int, int] = (92, 148, 252)  # Fond provisoire
PLAYER_RED: tuple[int, int, int] = (222, 68, 55)

# —— Physique du joueur ——
FPS: int = 60
PLAYER_SPEED: float = 2.5  # Vitesse horizontale en px par frame (avant upscale)
GRAVITY: float = 0.35      # Accélération gravitationnelle
JUMP_SPEED: float = -6.5   # Impulsion verticale du saut (négatif = vers le haut)

# —— Autres ——
GROUND_Y: int = WINDOW_HEIGHT  # Limite inférieure (sol) pour collision simple