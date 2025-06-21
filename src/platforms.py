from __future__ import annotations

from dataclasses import dataclass
import pygame
from settings import PLATFORM_TILESET_IMG, WINDOW_WIDTH, WINDOW_HEIGHT, PLAYER_SCALE


@dataclass
class Platform:
    """Simple platform with an image and collision rectangle."""

    rect: pygame.Rect
    image: pygame.Surface


def load_platform_image() -> pygame.Surface:
    """Load and return the platform sprite."""
    sheet = pygame.image.load(str(PLATFORM_TILESET_IMG)).convert_alpha()

    # Extract a larger portion of the tileset to avoid heavy pixelation.
    # The transparent margin on the left of the tileset starts around
    # x=0. The wooden platform graphics are located a bit further down
    # in the sheet. We grab a wide 512x64 slice starting at (64, 448)
    # so that scaling down keeps good quality.
    region = pygame.Rect(64, 448, 512, 64)
    img = sheet.subsurface(region).copy()

    # Scale down using the same factor as the characters for pixel-perfect
    # consistency.
    w, h = img.get_size()
    img = pygame.transform.scale(img, (int(w * PLAYER_SCALE), int(h * PLAYER_SCALE)))
    return img


def create_level_platforms() -> list[Platform]:
    """Create all platforms for the level."""
    img = load_platform_image()
    platforms: list[Platform] = []
    # Platform in the second screen to the right
    rect = img.get_rect(midbottom=(WINDOW_WIDTH + 80, WINDOW_HEIGHT - 40))
    platforms.append(Platform(rect, img))
    return platforms
