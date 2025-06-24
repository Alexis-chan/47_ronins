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

    # Extract a wider slice of the tileset to keep good quality when scaling
    # down.  The wooden platform graphics sit near the bottom of the sheet but
    # their exact vertical position changed between asset revisions.  To avoid
    # hardcoding a value that might fall outside the image, we compute the
    # region dynamically using the bottom 64 pixels of the tileset.
    h = sheet.get_height()
    region = pygame.Rect(64, max(0, h - 64), 512, 64)
    img = sheet.subsurface(region).copy()

    # Scale down using the same factor as the characters for pixel-perfect
    # consistency.
    w, h = img.get_size()
    img = pygame.transform.scale(img, (int(w * PLAYER_SCALE), int(h * PLAYER_SCALE)))
    return img


def load_ladder_image() -> pygame.Surface:
    """Load and scale the ladder sprite."""
    # The asset was renamed from "Echelle.png" to "Echelle_corde.png" in the
    # repository.  Update the path accordingly to avoid a FileNotFoundError.
    path = ASSETS_DIR / "niveaux" / "Echelle_corde.png"
    img = pygame.image.load(str(path)).convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.scale(img, (int(w * PLAYER_SCALE), int(h * PLAYER_SCALE)))
    return img


def create_level_platforms() -> list[Platform]:
    """Create all platforms for the level."""
    img = load_platform_image()
    platforms: list[Platform] = []

    # --- Screen 1 ---
    # Small platform near the start
    # The hero must be able to reach this first platform with a jump.  With the
    # current physics the maximum jump height is roughly 60 px, so we place the
    # platform slightly lower than before to keep it within reach.
    rect1 = img.get_rect(midbottom=(80, WINDOW_HEIGHT - 52))
    platforms.append(Platform(rect1, img))

    # Higher platform reached using a ladder
    rect2 = img.get_rect(midbottom=(160, WINDOW_HEIGHT - 100))
    platforms.append(Platform(rect2, img))

    # --- Screen 2 ---
    rect3 = img.get_rect(midbottom=(WINDOW_WIDTH + 120, WINDOW_HEIGHT - 70))
    platforms.append(Platform(rect3, img))

    rect4 = img.get_rect(midbottom=(WINDOW_WIDTH + 200, WINDOW_HEIGHT - 120))
    platforms.append(Platform(rect4, img))

    return platforms


def create_level_ladders(platforms: list[Platform]) -> list[Ladder]:
    """Create ladders for the level."""
    img = load_ladder_image()
    ladders: list[Ladder] = []

    # Ladder from platform 1 to platform 2
    if len(platforms) >= 2:
        upper = platforms[1]
        rect = img.get_rect(midbottom=(upper.rect.centerx, upper.rect.top))
        ladders.append(Ladder(rect, img))

    # Ladder leading to the highest platform
    if len(platforms) >= 4:
        high = platforms[3]
        rect2 = img.get_rect(midbottom=(high.rect.centerx, high.rect.top))
        ladders.append(Ladder(rect2, img))

    return ladders
