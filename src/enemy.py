from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pygame
from settings import PLAYER_SCALE, GRAVITY, GROUND_Y

@dataclass
class Enemy:
    pos: tuple[int, int]
    image_path: Path
    attack_path: Path | None = None
    health: int = 1
    patrol_left: int = 0
    patrol_right: int = 0
    speed: int = 1
    direction: int = 1

    facing_left: bool = True

    hitbox: pygame.Rect | None = None
    attacking: bool = False
    attack_timer: int = 0
    vel_y: float = 0.0
    on_ground: bool = True

    def __post_init__(self) -> None:
        img = pygame.image.load(str(self.image_path)).convert_alpha()
        scale = int(img.get_width() * PLAYER_SCALE)
        self.image = pygame.transform.scale(img, (scale, scale))
        self.rect = self.image.get_rect(midbottom=self.pos)
        self.hitbox = self.rect.copy()
        self.vel_y = 0.0
        self.on_ground = self.rect.bottom >= GROUND_Y
        if self.patrol_left == 0 and self.patrol_right == 0:
            self.patrol_left = self.rect.left - 40
            self.patrol_right = self.rect.right + 40
        if self.attack_path is not None:
            aimg = pygame.image.load(str(self.attack_path)).convert_alpha()
            self.attack_image = pygame.transform.scale(aimg, (scale, scale))
        else:
            self.attack_image = self.image

    def draw(self, surface: pygame.Surface, offset_x: int = 0) -> None:
        img = self.attack_image if self.attacking else self.image
        if not self.facing_left:
            img = pygame.transform.flip(img, True, False)
        rect = self.rect.move(-offset_x, 0)
        surface.blit(img, rect)

    def take_damage(self, amount: int) -> None:
        self.health = max(0, self.health - amount)

    def update(self, player_rect: pygame.Rect, platforms: list[pygame.Rect] | None = None) -> None:
        """Met à jour l'ennemi en faisant toujours face au joueur."""
        if self.health <= 0:
            return

        # Gravity
        if not self.on_ground:
            self.vel_y += GRAVITY
            self.hitbox.y += int(self.vel_y)
            if self.hitbox.bottom >= GROUND_Y:
                self.hitbox.bottom = GROUND_Y
                self.vel_y = 0
                self.on_ground = True
            if platforms:
                for plat in platforms:
                    will_land = (
                        self.vel_y >= 0
                        and self.hitbox.bottom - int(self.vel_y) <= plat.top < self.hitbox.bottom
                        and self.hitbox.right > plat.left
                        and self.hitbox.left < plat.right
                    )
                    if will_land:
                        self.hitbox.bottom = plat.top
                        self.vel_y = 0
                        self.on_ground = True
                        break
        self.rect.y = self.hitbox.y

        # Patrol left and right
        self.hitbox.x += self.direction * self.speed
        self.rect.x = self.hitbox.x
        if self.hitbox.left <= self.patrol_left or self.hitbox.right >= self.patrol_right:
            self.direction *= -1

        # oriente le Tengu vers le joueur cible
        self.facing_left = player_rect.centerx < self.hitbox.centerx

        if self.attack_timer > 0:
            self.attack_timer -= 1
            if self.attack_timer == 0:
                self.attacking = False
            return
        # Déclenche l'attaque si le joueur est à portée
        if abs(player_rect.centerx - self.hitbox.centerx) < 40 and abs(player_rect.centery - self.hitbox.centery) < self.hitbox.height:
            self.attacking = True
            self.attack_timer = 20
            self.facing_left = player_rect.centerx < self.hitbox.centerx

    def get_attack_rect(self) -> pygame.Rect | None:
        if not self.attacking or self.attack_timer > 10:
            return None
        width = 16
        height = self.hitbox.height // 2
        y = self.hitbox.centery - height // 2
        if self.facing_left:
            x = self.hitbox.left - width
        else:
            x = self.hitbox.right
        return pygame.Rect(x, y, width, height)
