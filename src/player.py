"""player.py
Contient la classe Player représentant le chat humanoïde contrôlable.
Gestion :
 • entrée clavier (gauche/droite/saut)
 • physique simple (gravité, collisions avec le sol)
 • rendu du sprite provisoire (rectangle rouge)
"""

from dataclasses import dataclass
import pygame
from settings import (
    PLAYER_RED,
    PLAYER_SPEED,
    GRAVITY,
    JUMP_SPEED,
    WINDOW_HEIGHT,
)

@dataclass
class Player:
    """Joueur contrôlable côté client."""

    rect: pygame.Rect
    vel: pygame.Vector2
    on_ground: bool = False

    def __init__(self, pos: tuple[int, int]):
        width, height = 16, 20  # Dimensions temporaires du sprite
        self.rect = pygame.Rect(pos[0], pos[1], width, height)
        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False

    # ————————————————————
    # Boucle d’update
    # ————————————————————

    def handle_input(self, pressed: pygame.key.ScancodeWrapper) -> None:
        """Mise à jour de la vitesse horizontale en fonction des touches pressées."""
        self.vel.x = 0  # Annule l’inertie à chaque frame pour un contrôle précis
        if pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
            self.vel.x = -PLAYER_SPEED
        if pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
            self.vel.x = PLAYER_SPEED

        # Saut : possible uniquement quand le joueur est au sol
        if (pressed[pygame.K_z] or pressed[pygame.K_SPACE]) and self.on_ground:
            self.vel.y = JUMP_SPEED
            self.on_ground = False

    def apply_gravity(self) -> None:
        """Applique la gravité lorsque le joueur est en l’air."""
        if not self.on_ground:
            self.vel.y += GRAVITY

    def update(self, pressed: pygame.key.ScancodeWrapper) -> None:
        """Met à jour la position et l’état du joueur pour la frame courante."""
        self.handle_input(pressed)
        self.apply_gravity()

        # Déplacement horizontal
        self.rect.x += int(self.vel.x)

        # Déplacement vertical
        self.rect.y += int(self.vel.y)

        # Collision simple avec le sol (bas de la fenêtre)
        if self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.vel.y = 0
            self.on_ground = True

    # ————————————————————
    # Rendu
    # ————————————————————

    def draw(self, surface: pygame.Surface) -> None:
        """Dessine le sprite provisoire (rectangle)."""
        pygame.draw.rect(surface, PLAYER_RED, self.rect)