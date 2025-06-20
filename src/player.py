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
    jump_phase: str = "stand"
    invincible_time: int = 0
    invincible: bool = False

    attack_type: str = ""
    name: str = "player"

    def __init__(self, pos: tuple[int, int], asset_paths: dict[str, Path], name: str = "player"):
        """Initialise le joueur avec les sprites du personnage choisi."""

        self.name = name

        self.images = {}
        if "stand" in asset_paths:
            self.images["stand"] = pygame.image.load(
                str(asset_paths["stand"])
            ).convert_alpha()
        if "sit" in asset_paths:
            self.images["sit"] = pygame.image.load(
                str(asset_paths["sit"])
            ).convert_alpha()
        if "hurt" in asset_paths:
            self.images["hurt"] = pygame.image.load(
                str(asset_paths["hurt"])
            ).convert_alpha()

        # Réduction des sprites fixes
        for key, img in self.images.items():
            w = int(img.get_width() * PLAYER_SCALE)
            h = int(img.get_height() * PLAYER_SCALE)
            self.images[key] = pygame.transform.scale(img, (w, h))

        # Chargement des animations
        self.animations = {}
        for key in ("walk", "jump", "attack", "kick", "jumpkick"):
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
        self.attack_type = ""
        self.health = 6 if name.lower() == "koji" else 5
        self.jump_phase = "stand"
        self.invincible_time = 0
        self.invincible = False

    def _load_frames(self, paths: Path | list[Path]) -> list[pygame.Surface]:
        """Charge des frames depuis une feuille de sprites ou plusieurs images."""

        if isinstance(paths, (list, tuple)):
            frames: list[pygame.Surface] = []
            for p in paths:
                img = pygame.image.load(str(p)).convert_alpha()
                scale = int(img.get_width() * PLAYER_SCALE)
                frames.append(pygame.transform.scale(img, (scale, scale)))
            return frames

        sheet = pygame.image.load(str(paths)).convert_alpha()
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

    def get_attack_rect(self) -> pygame.Rect | None:
        """Retourne la zone d'attaque active."""
        if not self.is_attacking:
            return None
        width = 16
        height = self.hitbox.height // 2
        y = self.hitbox.centery - height // 2
        if self.facing_left:
            x = self.hitbox.left - width
        else:
            x = self.hitbox.right
        return pygame.Rect(x, y, width, height)

    def attack_damage(self) -> int:
        """Dégâts infligés par l'attaque courante."""
        if self.attack_type == "kick":
            return 2
        if self.name.lower() == "oishi":
            return 3
        # coup de poing par défaut
        return 1

    def take_damage(self, amount: int, from_left: bool = True) -> None:
        """Réduit la vie du joueur en appliquant un knockback."""
        if self.invincible_time > 0 or self.invincible:
            return
        self.health = max(0, self.health - amount)
        self.invincible_time = 60  # ~1 seconde à 60 FPS
        self.vel.x = 2 if from_left else -2
        if "hurt" in self.images:
            self.current_image = self.images["hurt"]
        self.frame_index = 0

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
            self.jump_phase = "start"
            self.frame_index = 0
            self.jump_sound.play()

    def apply_gravity(self) -> None:
        """Applique la gravité lorsque le joueur est en l’air."""
        if not self.on_ground:
            self.vel.y += GRAVITY

    def start_attack(self) -> None:
        """Déclenche l'animation d'attaque (poing ou arme)."""
        if not self.is_attacking:
            self.is_attacking = True
            self.frame_index = 0
            self.invincible = True
            if self.name.lower() == "oishi":
                self.attack_type = "attack"
            else:
                self.attack_type = "attack"
            if not self.on_ground and "jumpkick" in self.animations:
                self.attack_type = "jumpkick"
            if self.name.lower() == "koji" and self.on_ground:
                # avance légèrement lors du coup de poing
                self.hitbox.x += 3 if not self.facing_left else -3

    def start_kick(self) -> None:
        """Déclenche une attaque de type coup de pied."""
        if not self.is_attacking and "kick" in self.animations:
            self.is_attacking = True
            self.frame_index = 0
            self.invincible = True
            self.attack_type = "kick"
            if not self.on_ground and "jumpkick" in self.animations:
                self.attack_type = "jumpkick"

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

        if self.invincible_time > 0:
            self.invincible_time -= 1
            # ralentit progressivement le mouvement de recul
            self.vel.x *= 0.9
        else:
            self.handle_input(pressed, controls)

        # Déplacement horizontal
        self.hitbox.x += int(self.vel.x)
        if self.hitbox.left < 0:
            self.hitbox.left = 0

        if self.on_ground and platforms:
            on_plat = False
            for plat in platforms:
                if self.hitbox.bottom == plat.top and self.hitbox.colliderect(plat):
                    on_plat = True
                    break
            if not on_plat and self.hitbox.bottom < WINDOW_HEIGHT:
                self.on_ground = False

        self.apply_gravity()

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
            if not self.is_attacking and "stand" in self.images:
                self.current_image = self.images["stand"]
                # reset animation index to avoid flicker when landing
                self.frame_index = 0
            self.jump_phase = "stand"

        if self.invincible_time > 0 and "hurt" in self.images:
            self.current_image = self.images["hurt"]
            self.frame_index = 0
        elif self.is_attacking:
            state = self.attack_type if self.attack_type else "attack"
            if state in self.animations:
                if (
                    state == "jumpkick"
                    and pressed[controls.get("kick", pygame.K_d)]
                    and int(self.frame_index) >= len(self.animations[state]) - 1
                ):
                    self.current_image = self.animations[state][-1]
                else:
                    self._animate(state, loop=False)
                if not self.is_attacking:
                    self.invincible = False
            else:
                self.is_attacking = False
                self.invincible = False
        elif self.jump_phase == "start":
            frames = self.animations.get("jump")
            if frames:
                self.current_image = frames[0]
            self.jump_phase = "midair"
        elif not self.on_ground:
            frames = self.animations.get("jump")
            if frames:
                self.current_image = frames[1]
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

        if self.invincible_time <= 0 and not self.is_attacking:
            self.invincible = False

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
        """Dessine les coeurs de vie en haut à gauche sur deux lignes max."""
        max_per_row = 10
        for i in range(self.health):
            row = i // max_per_row
            col = i % max_per_row
            x = 5 + col * (heart.get_width() + 2)
            y = 5 + row * (heart.get_height() + 2)
            surface.blit(heart, (x, y))
