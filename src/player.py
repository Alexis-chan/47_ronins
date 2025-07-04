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
    LANDING_TIME,
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
    landing_timer: int = 0
    on_ladder: bool = False
    jump_speed: float = JUMP_SPEED

    attack_type: str = ""
    name: str = "player"

    def __init__(
        self,
        pos: tuple[int, int],
        asset_paths: dict[str, Path],
        name: str = "player",
        jump_speed: float = JUMP_SPEED,
    ):
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
        self.jump_speed = jump_speed
        self.is_attacking = False
        self.attack_type = ""
        self.health = 6 if name.lower() == "koji" else 5
        self.jump_phase = "stand"
        self.invincible_time = 0
        self.invincible = False
        self.landing_timer = 0
        self.on_ladder = False

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
            # frames disposées horizontalement
            num_frames = max(1, round(w / h))
            frame_w = w // num_frames
            frame_h = h
            regions = [
                pygame.Rect(i * frame_w, 0, frame_w, frame_h)
                for i in range(num_frames)
            ]
        else:
            # frames disposées verticalement
            num_frames = max(1, round(h / w))
            frame_w = w
            frame_h = h // num_frames
            regions = [
                pygame.Rect(0, i * frame_h, frame_w, frame_h)
                for i in range(num_frames)
            ]

        frames: list[pygame.Surface] = []
        for rect in regions:
            region = sheet.subsurface(rect).copy()
            w_scaled = int(rect.width * PLAYER_SCALE)
            h_scaled = int(rect.height * PLAYER_SCALE)
            region = pygame.transform.scale(region, (w_scaled, h_scaled))
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
        self.is_attacking = False
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
            self.vel.y = self.jump_speed
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
        if not self.is_attacking and self.invincible_time <= 0:
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
        if not self.is_attacking and self.invincible_time <= 0 and "kick" in self.animations:
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
        ladders: list[pygame.Rect] | None = None,
        walls: list[pygame.Rect] | None = None,
        controls: dict[str, int] | None = None,
    ) -> None:
        """Met à jour la position et l’état du joueur pour la frame courante."""

        if controls is None:
            controls = {}

        prev_on_ground = self.on_ground

        self.handle_input(pressed, controls)
        if self.invincible_time > 0:
            self.invincible_time -= 1

        # Horizontal movement
        self.hitbox.x += int(self.vel.x)
        if self.hitbox.left < 0:
            self.hitbox.left = 0
        if walls:
            for wall in walls:
                if self.hitbox.colliderect(wall):
                    if self.vel.x > 0:
                        self.hitbox.right = wall.left
                    elif self.vel.x < 0:
                        self.hitbox.left = wall.right

        # Ladder check
        self.on_ladder = False
        active_ladder = None
        if ladders:
            for lad in ladders:
                if self.hitbox.colliderect(lad):
                    self.on_ladder = True
                    active_ladder = lad
                    break

        if self.on_ladder:
            self.hitbox.centerx = active_ladder.centerx
            if pressed[controls.get("up", pygame.K_UP)]:
                self.vel.y = -PLAYER_SPEED
            elif pressed[controls.get("down", pygame.K_DOWN)]:
                self.vel.y = PLAYER_SPEED
            else:
                self.vel.y = 0
        else:
            self.apply_gravity()

        # Vertical movement
        self.hitbox.y += int(self.vel.y)
        self.on_ground = False

        # Floor collision
        if self.hitbox.bottom >= WINDOW_HEIGHT:
            self.hitbox.bottom = WINDOW_HEIGHT
            self.vel.y = 0
            self.on_ground = True

        if platforms:
            for plat in platforms:
                move_y = int(self.vel.y)
                prev_bottom = self.hitbox.bottom - move_y

                will_cross = self.vel.y >= 0 and prev_bottom <= plat.top < self.hitbox.bottom
                overlap = self.hitbox.right > plat.left and self.hitbox.left < plat.right

                if will_cross and overlap:
                    self.hitbox.bottom = plat.top
                    self.vel.y = 0
                    self.on_ground = True
                    break

                elif abs(self.hitbox.bottom - plat.top) <= 1 and self.vel.y >= 0 and overlap:
                    self.hitbox.bottom = plat.top
                    self.vel.y = 0
                    self.on_ground = True
                    break

        just_landed = not prev_on_ground and self.on_ground
        if just_landed:
            self.is_attacking = False
            self.landing_timer = LANDING_TIME
            frames = self.animations.get("jump")
            if frames and len(frames) > 2:
                self.current_image = frames[2]
            elif "stand" in self.images:
                self.current_image = self.images["stand"]
            self.frame_index = 0
            self.jump_phase = "landing"

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
        elif self.jump_phase == "landing":
            frames = self.animations.get("jump")
            if frames and len(frames) > 2:
                self.current_image = frames[2]
            self.landing_timer -= 1
            if self.landing_timer <= 0:
                self.jump_phase = "stand"
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

    def draw(self, surface: pygame.Surface, offset_x: int = 0) -> None:
        """Dessine le sprite actuel."""
        image = self.current_image
        if self.facing_left:
            image = pygame.transform.flip(image, True, False)

        img_rect = image.get_rect(midbottom=(self.hitbox.midbottom[0] - offset_x, self.hitbox.midbottom[1]))
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
