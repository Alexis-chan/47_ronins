from __future__ import annotations

from dataclasses import dataclass
import pygame
from settings import (
    PLATFORM_TILESET_IMG,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    PLAYER_SCALE,
    ASSETS_DIR,
)


@dataclass
class Platform:
    """Simple platform with an image and collision rectangle."""

    rect: pygame.Rect
    image: pygame.Surface


@dataclass
class Ladder:
    """Climbable ladder allowing the player to reach higher platforms."""

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


def load_ladder_image() -> pygame.Surface:
    """Load and scale the ladder sprite."""
    path = ASSETS_DIR / "niveaux" / "Echelle.png"
    img = pygame.image.load(str(path)).convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.scale(img, (int(w * PLAYER_SCALE), int(h * PLAYER_SCALE)))
    return img


def create_level_platforms() -> list[Platform]:
    """Create all platforms for the level."""
    img = load_platform_image()
    platforms: list[Platform] = []

    # First platform placed in the first screen
    rect = img.get_rect(midbottom=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60))
    platforms.append(Platform(rect, img))

    # Second platform can only be reached from the first one
    rect2 = img.get_rect(midbottom=(WINDOW_WIDTH // 2 + 60, WINDOW_HEIGHT - 100))
    platforms.append(Platform(rect2, img))

    # Third platform on the second screen
    rect3 = img.get_rect(midbottom=(WINDOW_WIDTH + 100, WINDOW_HEIGHT - 80))
    platforms.append(Platform(rect3, img))

    return platforms


def create_level_ladders(platforms: list[Platform]) -> list[Ladder]:
    """Create ladders for the level."""
    img = load_ladder_image()
    ladders: list[Ladder] = []

    # Ladder leading to the third platform
    third = platforms[-1]
    rect = img.get_rect(midbottom=(third.rect.centerx, third.rect.top))
    ladders.append(Ladder(rect, img))

    return ladders
