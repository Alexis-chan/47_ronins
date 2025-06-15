"""player.py
Contient la classe Player représentant le chat humanoïde contrôlable.
Gestion :
 • entrée clavier (gauche/droite/saut)
 • physique simple (gravité, collisions avec le sol)
 • rendu du sprite provisoire (rectangle rouge)
"""

from dataclasses import dataclass
from pathlib import Path
import pygame
from settings import (
    PLAYER_RED,
    PLAYER_SPEED,
    GRAVITY,
    JUMP_SPEED,
    WINDOW_HEIGHT,
    PLAYER_SCALE,
    SPRITE_SIZE,
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
    animations: dict[str, list[pygame.Surface]] | None = None
    state: str = "stand"
    frame_index: int = 0
    frame_delay: int = 5
    frame_timer: int = 0

    def __init__(self, pos: tuple[int, int]):
        self.animations = {
            "stand": self._load_frames(PLAYER_STAND_IMG),
            "walk": self._load_frames(PLAYER_WALK_IMG),
            "jump": self._load_frames(PLAYER_JUMP_IMG),
            "sit": self._load_frames(PLAYER_SIT_IMG),
        }

        image = self.animations["stand"][0]
        width, height = image.get_size()
        self.rect = pygame.Rect(pos[0], pos[1], width, height)
        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False
        self.facing_left = False
        self.jump_sound = pygame.mixer.Sound(str(JUMP_SOUND_FILE))

    def _load_frames(self, path: Path) -> list[pygame.Surface]:
        """Découpe une sprite sheet en frames redimensionnées."""
        sheet = pygame.image.load(str(path)).convert_alpha()
        frames: list[pygame.Surface] = []
        for y in range(0, sheet.get_height(), SPRITE_SIZE):
            for x in range(0, sheet.get_width(), SPRITE_SIZE):
                rect = pygame.Rect(x, y, SPRITE_SIZE, SPRITE_SIZE)
                frame = sheet.subsurface(rect)
                w = int(SPRITE_SIZE * PLAYER_SCALE)
                h = int(SPRITE_SIZE * PLAYER_SCALE)
                frames.append(pygame.transform.scale(frame, (w, h)))
        return frames

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
            self.state = "jump"
        elif pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
            self.state = "sit"
        elif self.vel.x != 0:
            self.state = "walk"
        else:
            self.state = "stand"

        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.state])

    # ————————————————————
    # Rendu
    # ————————————————————

    def draw(self, surface: pygame.Surface) -> None:
        """Dessine le sprite actuel."""
        image = self.animations[self.state][self.frame_index]
        if self.facing_left:
            image = pygame.transform.flip(image, True, False)
        surface.blit(image, self.rect)
