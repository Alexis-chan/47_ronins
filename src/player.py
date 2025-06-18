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
    PLAYER_SPEED,
    GRAVITY,
    JUMP_SPEED,
    WINDOW_HEIGHT,
    PLAYER_SCALE,
    JUMP_SOUND_FILE,
)

@dataclass
class Player:
    """Joueur contrôlable côté client."""

    hitbox: pygame.Rect
    vel: pygame.Vector2
    on_ground: bool = False
    facing_left: bool = False
    images: dict[str, pygame.Surface] | None = None
    animations: dict[str, list[pygame.Surface]] | None = None
    current_image: pygame.Surface | None = None
    frame_index: float = 0.0
    animation_speed: float = 0.2
    is_attacking: bool = False
    health: int = 5

    def __init__(self, pos: tuple[int, int], asset_paths: dict[str, Path]):
        """Initialise le joueur avec les sprites du personnage choisi."""

        self.images = {}
        if "stand" in asset_paths:
            self.images["stand"] = pygame.image.load(
                str(asset_paths["stand"])
            ).convert_alpha()
        if "sit" in asset_paths:
            self.images["sit"] = pygame.image.load(
                str(asset_paths["sit"])
            ).convert_alpha()

        # Réduction des sprites fixes
        for key, img in self.images.items():
            w = int(img.get_width() * PLAYER_SCALE)
            h = int(img.get_height() * PLAYER_SCALE)
            self.images[key] = pygame.transform.scale(img, (w, h))

        # Chargement des animations
        self.animations = {}
        for key in ("walk", "jump", "attack"):
            if key in asset_paths:
                self.animations[key] = self._load_frames(asset_paths[key])

        self.current_image = self.images["stand"]
        # Hitbox utilisée pour la physique, indépendante de la taille du sprite
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 32)
        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False
        self.facing_left = False
        self.jump_sound = pygame.mixer.Sound(str(JUMP_SOUND_FILE))
        self.is_attacking = False
        self.health = 5

    def _load_frames(self, path: Path) -> list[pygame.Surface]:
        """Charge un sprite sheet en détectant automatiquement son découpage."""

        sheet = pygame.image.load(str(path)).convert_alpha()
        w, h = sheet.get_width(), sheet.get_height()

        if w >= h:
            frame_size = h
            num_frames = w // frame_size
            regions = [
                pygame.Rect(i * frame_size, 0, frame_size, frame_size)
                for i in range(num_frames)
            ]
        else:
            frame_size = w
            num_frames = h // frame_size
            regions = [
                pygame.Rect(0, i * frame_size, frame_size, frame_size)
                for i in range(num_frames)
            ]

        frames: list[pygame.Surface] = []
        for rect in regions:
            region = sheet.subsurface(rect).copy()
            scale = int(frame_size * PLAYER_SCALE)
            region = pygame.transform.scale(region, (scale, scale))
            frames.append(region)

        return frames

    def _animate(self, state: str, loop: bool = True) -> None:
        """Met à jour l'image courante d'une animation."""
        frames = self.animations[state]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(frames):
            if loop:
                self.frame_index = 0
            else:
                self.frame_index = len(frames) - 1
                self.is_attacking = False
        self.current_image = frames[int(self.frame_index)]

    # ————————————————————
    # Boucle d’update
    # ————————————————————

    def handle_input(self, pressed: pygame.key.ScancodeWrapper, controls: dict[str, int]) -> None:
        """Mise à jour de la vitesse horizontale en fonction des touches pressées."""

        self.vel.x = 0  # Annule l’inertie à chaque frame pour un contrôle précis
        if pressed[controls.get("left", pygame.K_LEFT)]:
            self.vel.x = -PLAYER_SPEED
            self.facing_left = True
        if pressed[controls.get("right", pygame.K_RIGHT)]:
            self.vel.x = PLAYER_SPEED
            self.facing_left = False

        # Saut : possible uniquement quand le joueur est au sol
        if pressed[controls.get("jump", pygame.K_SPACE)] and self.on_ground:
            self.vel.y = JUMP_SPEED
            self.on_ground = False
            self.jump_sound.play()

    def apply_gravity(self) -> None:
        """Applique la gravité lorsque le joueur est en l’air."""
        if not self.on_ground:
            self.vel.y += GRAVITY

    def start_attack(self) -> None:
        """Déclenche l'animation d'attaque."""
        if not self.is_attacking:
            self.is_attacking = True
            self.frame_index = 0

    def update(
        self,
        pressed: pygame.key.ScancodeWrapper,
        platforms: list[pygame.Rect] | None = None,
        controls: dict[str, int] | None = None,
    ) -> None:
        """Met à jour la position et l’état du joueur pour la frame courante."""

        if controls is None:
            controls = {}

        prev_on_ground = self.on_ground

        self.handle_input(pressed, controls)
        self.apply_gravity()

        # Déplacement horizontal
        self.hitbox.x += int(self.vel.x)
        if self.hitbox.left < 0:
            self.hitbox.left = 0

        # Déplacement vertical
        self.hitbox.y += int(self.vel.y)

        # Collision simple avec le sol (bas de la fenêtre)
        if self.hitbox.bottom >= WINDOW_HEIGHT:
            self.hitbox.bottom = WINDOW_HEIGHT
            self.vel.y = 0
            self.on_ground = True

        if platforms:
            for plat in platforms:
                prev_bottom = self.hitbox.bottom - int(self.vel.y)
                if (
                    self.hitbox.colliderect(plat)
                    and prev_bottom <= plat.top
                    and self.vel.y >= 0
                ):
                    self.hitbox.bottom = plat.top
                    self.vel.y = 0
                    self.on_ground = True

        just_landed = not prev_on_ground and self.on_ground
        if just_landed:
            jump_frames = self.animations.get("jump")
            if jump_frames:
                self.frame_index = len(jump_frames) - 1
                self.current_image = jump_frames[-1]

        if self.is_attacking:
            self._animate("attack", loop=False)
        elif not self.on_ground:
            if self.frame_index == 0 and self.animations.get("jump"):
                # Première frame déjà affichée, passer à la suivante
                self.frame_index = 1
            if self.animations.get("jump"):
                self._animate("jump", loop=True)
        elif just_landed:
            # Garder l'image d'atterrissage une frame
            pass
        elif pressed[controls.get("down", pygame.K_DOWN)]:
            if "sit" in self.images:
                self.current_image = self.images["sit"]
            self.frame_index = 0
        elif self.vel.x != 0:
            if "walk" in self.animations:
                self._animate("walk")
        else:
            if "stand" in self.images:
                self.current_image = self.images["stand"]
            self.frame_index = 0

    # ————————————————————
    # Rendu
    # ————————————————————

    def draw(self, surface: pygame.Surface) -> None:
        """Dessine le sprite actuel."""
        image = self.current_image
        if self.facing_left:
            image = pygame.transform.flip(image, True, False)

        img_rect = image.get_rect(midbottom=self.hitbox.midbottom)
        surface.blit(image, img_rect)

    def draw_health(self, surface: pygame.Surface, heart: pygame.Surface) -> None:
        """Dessine les coeurs de vie en haut à gauche."""
        for i in range(self.health):
            x = 5 + i * (heart.get_width() + 2)
            surface.blit(heart, (x, 5))
