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


@dataclass
class Staircase:
    """Decorative staircase used to reach a higher platform."""

    rect: pygame.Rect
    image: pygame.Surface


@dataclass
class Wall:
    """Solid vertical wall blocking the player."""

    rect: pygame.Rect
    image: pygame.Surface


def load_platform_image() -> pygame.Surface:
    """Load and return the platform sprite."""
    sheet = pygame.image.load(str(PLATFORM_TILESET_IMG)).convert_alpha()

    # Extract a wider slice of the tileset to keep good quality when scaling
    # down.  The wooden platform graphics sit near the bottom of the sheet but
    # their exact vertical position changed between asset revisions.  To avoid
    # hardcoding a value that might fall outside the image, we compute the
    # region dynamically using the bottom 256 pixels of the tileset to ensure
    # the scaled image remains visible.
    h = sheet.get_height()
    region = pygame.Rect(64, max(0, h - 256), 512, 256)
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


def load_stair_image() -> pygame.Surface:
    """Load and scale the wooden staircase sprite."""
    path = ASSETS_DIR / "niveaux" / "Stair_wood_1.png"
    img = pygame.image.load(str(path)).convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.scale(img, (int(w * PLAYER_SCALE), int(h * PLAYER_SCALE)))
    return img


def load_wall_image() -> pygame.Surface:
    """Load and scale the wooden wall sprite."""
    path = ASSETS_DIR / "niveaux" / "Wall_wood_side.png"
    img = pygame.image.load(str(path)).convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.scale(img, (int(w * PLAYER_SCALE), int(h * PLAYER_SCALE)))
    return img


def create_level_platforms() -> list[Platform]:
    """Create all platforms for the level."""
    img = load_platform_image()
    platforms: list[Platform] = []

    # --- Screen 1 ---
    rect1 = img.get_rect(midbottom=(60, WINDOW_HEIGHT - 48))
    platforms.append(Platform(rect1, img))

    # Elevated walkway accessed via ladder
    rect2 = img.get_rect(midbottom=(120, WINDOW_HEIGHT - 112))
    platforms.append(Platform(rect2, img))
    rect3 = img.get_rect(midbottom=(160, WINDOW_HEIGHT - 112))
    platforms.append(Platform(rect3, img))

    # --- Screen 2 --- (continuation of high path)
    rect4 = img.get_rect(midbottom=(WINDOW_WIDTH + 40, WINDOW_HEIGHT - 112))
    platforms.append(Platform(rect4, img))
    rect5 = img.get_rect(midbottom=(WINDOW_WIDTH + 120, WINDOW_HEIGHT - 112))
    platforms.append(Platform(rect5, img))

    # Ground platform after a gap
    rect6 = img.get_rect(midbottom=(WINDOW_WIDTH + 220, WINDOW_HEIGHT - 48))
    platforms.append(Platform(rect6, img))

    # --- Screen 3 --- staircase leads back up
    rect7 = img.get_rect(midbottom=(2 * WINDOW_WIDTH + 80, WINDOW_HEIGHT - 96))
    platforms.append(Platform(rect7, img))
    rect8 = img.get_rect(midbottom=(2 * WINDOW_WIDTH + 160, WINDOW_HEIGHT - 96))
    platforms.append(Platform(rect8, img))

    # --- Screen 4 --- final high path
    rect9 = img.get_rect(midbottom=(3 * WINDOW_WIDTH + 80, WINDOW_HEIGHT - 120))
    platforms.append(Platform(rect9, img))
    rect10 = img.get_rect(midbottom=(3 * WINDOW_WIDTH + 160, WINDOW_HEIGHT - 120))
    platforms.append(Platform(rect10, img))

    return platforms


def create_level_ladders(platforms: list[Platform]) -> list[Ladder]:
    """Create ladders for the level."""
    img = load_ladder_image()
    ladders: list[Ladder] = []

    if len(platforms) >= 10:
        # Ladder at the start to reach the high path
        start_high = platforms[1]
        rect1 = img.get_rect(midbottom=(start_high.rect.centerx, start_high.rect.top))
        ladders.append(Ladder(rect1, img))

        # Ladder at the end to descend from the final platform
        end_high = platforms[-1]
        rect2 = img.get_rect(midbottom=(end_high.rect.centerx, end_high.rect.top))
        ladders.append(Ladder(rect2, img))

    return ladders


def create_level_stairs() -> list[Staircase]:
    """Create the decorative staircase for the level."""
    img = load_stair_image()
    stairs: list[Staircase] = []

    # First staircase used to leave the upper path
    rect1 = img.get_rect(midbottom=(WINDOW_WIDTH + 160, WINDOW_HEIGHT))
    stairs.append(Staircase(rect1, img))

    # Second staircase bringing the player back up later in the level
    rect2 = img.get_rect(midbottom=(2 * WINDOW_WIDTH + 40, WINDOW_HEIGHT))
    stairs.append(Staircase(rect2, img))

    return stairs


def create_level_walls() -> list[Wall]:
    """Create blocking walls for the level."""
    img = load_wall_image()
    walls: list[Wall] = []

    # Wall at the start forcing ladder use
    rect1 = img.get_rect(midbottom=(100, WINDOW_HEIGHT))
    walls.append(Wall(rect1, img))

    # Wall before the final ladder
    rect2 = img.get_rect(midbottom=(3 * WINDOW_WIDTH + 120, WINDOW_HEIGHT))
    walls.append(Wall(rect2, img))

    return walls
