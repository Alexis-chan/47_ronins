from __future__ import annotations

from dataclasses import dataclass
import pygame
from settings import PLATFORM_TILESET_IMG, WINDOW_WIDTH, WINDOW_HEIGHT


@dataclass
class Platform:
    """Simple platform with an image and collision rectangle."""

    rect: pygame.Rect
    image: pygame.Surface


def load_platform_image() -> pygame.Surface:
    """Load and return the platform sprite."""
    sheet = pygame.image.load(str(PLATFORM_TILESET_IMG)).convert_alpha()
    img = sheet.subsurface(pygame.Rect(0, 0, 32, 8))
    return pygame.transform.scale(img, (32, 8))


def create_level_platforms() -> list[Platform]:
    """Create all platforms for the level."""
    img = load_platform_image()
    platforms: list[Platform] = []
    # Platform in the second screen to the right
    rect = img.get_rect(midbottom=(WINDOW_WIDTH + 80, WINDOW_HEIGHT - 40))
    platforms.append(Platform(rect, img))
    return platforms
