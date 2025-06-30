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


def load_stair_image() -> pygame.Surface:
    """Load and scale the wooden stair sprite."""
    path = ASSETS_DIR / "niveaux" / "Stair_wood_1.png"
    img = pygame.image.load(str(path)).convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.scale(img, (int(w * PLAYER_SCALE), int(h * PLAYER_SCALE)))
    return img


def create_level_platforms() -> list[Platform]:
    """Create all platforms for the level following the reference layout."""
    base = load_platform_image()
    stair_src = load_stair_image()

    platforms: list[Platform] = []

    def add_platform(tiles: int, x: int, bottom: int) -> None:
        width = base.get_width() * tiles
        img = pygame.transform.scale(base, (width, base.get_height()))
        rect = img.get_rect(midbottom=(x, bottom))
        platforms.append(Platform(rect, img))

    # Bottom left small platform
    add_platform(2, 160, 206)

    # Central mid platform with torii
    add_platform(2, 480, 171)

    # Upper left platform reached by the stairs
    add_platform(2, 640, 137)

    # Large upper right platform
    add_platform(5, 1344, 137)

    # Stairs descending to the left (10 steps)
    steps = 10
    step_w = (640 - 448) // steps or 1
    step_h = (223 - 137) // steps or 1
    for i in range(steps):
        img = pygame.transform.scale(stair_src, (step_w, step_h))
        x = 640 - i * step_w
        bottom = 137 + (i + 1) * step_h
        rect = img.get_rect(midbottom=(x, bottom))
        platforms.append(Platform(rect, img))

    return platforms


def create_level_ladders(platforms: list[Platform]) -> list[Ladder]:
    """Create ladders for the level."""
    raw = load_ladder_image()
    ladders: list[Ladder] = []

    # Rope ladder on the far right platform
    height = int(WINDOW_HEIGHT - 154)
    img = pygame.transform.scale(raw, (raw.get_width(), height))
    rect = img.get_rect(midbottom=(1664, WINDOW_HEIGHT))
    ladders.append(Ladder(rect, img))

    return ladders
