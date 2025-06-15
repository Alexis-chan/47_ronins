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
    PLAYER_STAND_IMG,
    PLAYER_WALK_IMG,
    PLAYER_JUMP_IMG,
    PLAYER_SIT_IMG,
    JUMP_SOUND_FILE,
)

@dataclass
class Player:
    """Joueur contrôlable côté client."""

    rect: pygame.Rect
    vel: pygame.Vector2
    on_ground: bool = False
    facing_left: bool = False
    images: dict[str, pygame.Surface] | None = None
    current_image: pygame.Surface | None = None

    def __init__(self, pos: tuple[int, int]):
        self.images = {
            "stand": pygame.image.load(PLAYER_STAND_IMG).convert_alpha(),
            "walk": pygame.image.load(PLAYER_WALK_IMG).convert_alpha(),
            "jump": pygame.image.load(PLAYER_JUMP_IMG).convert_alpha(),
            "sit": pygame.image.load(PLAYER_SIT_IMG).convert_alpha(),
        }
        self.current_image = self.images["stand"]
        width, height = self.current_image.get_size()
        self.rect = pygame.Rect(pos[0], pos[1], width, height)
        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False
        self.facing_left = False
        self.jump_sound = pygame.mixer.Sound(JUMP_SOUND_FILE)

    # ————————————————————
    # Boucle d’update
    # ————————————————————

    def handle_input(self, pressed: pygame.key.ScancodeWrapper) -> None:
        """Mise à jour de la vitesse horizontale en fonction des touches pressées."""
        self.vel.x = 0  # Annule l’inertie à chaque frame pour un contrôle précis
        if pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
            self.vel.x = -PLAYER_SPEED
            self.facing_left = True
        if pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
            self.vel.x = PLAYER_SPEED
            self.facing_left = False

        # Saut : possible uniquement quand le joueur est au sol
        if (pressed[pygame.K_z] or pressed[pygame.K_SPACE]) and self.on_ground:
            self.vel.y = JUMP_SPEED
            self.on_ground = False
            self.jump_sound.play()

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

        if not self.on_ground:
            self.current_image = self.images["jump"]
        elif pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
            self.current_image = self.images["sit"]
        elif self.vel.x != 0:
            self.current_image = self.images["walk"]
        else:
            self.current_image = self.images["stand"]

    # ————————————————————
    # Rendu
    # ————————————————————

    def draw(self, surface: pygame.Surface) -> None:
        """Dessine le sprite actuel."""
        image = self.current_image
        if self.facing_left:
            image = pygame.transform.flip(image, True, False)
        surface.blit(image, self.rect)
