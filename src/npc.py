from dataclasses import dataclass
from pathlib import Path
import pygame
from settings import PLAYER_SCALE

@dataclass
class NPC:
    """Simple non-playable character displayed in the level."""

    pos: tuple[int, int]
    image_path: Path

    def __post_init__(self) -> None:
        img = pygame.image.load(str(self.image_path)).convert_alpha()
        scale = int(img.get_width() * PLAYER_SCALE)
        self.image = pygame.transform.scale(img, (scale, scale))
        self.rect = self.image.get_rect(midbottom=self.pos)

    def draw(self, surface: pygame.Surface, offset_x: int = 0) -> None:
        surface.blit(self.image, self.rect.move(-offset_x, 0))
