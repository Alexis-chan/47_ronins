"""main.py
Point d’entrée du jeu : initialisation de Pygame, création de la fenêtre, boucle principale.
La scène est dessinée sur une surface 320×240 puis mise à l’échelle x3 → 960×720
pour un rendu pixel‑perfect sans flou.
"""

from __future__ import annotations

import sys
from pathlib import Path
import pygame

from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
    FPS,
    BACKGROUND_IMG,
    TILESET_IMG,
    MUSIC_FILE,
    FULLSCREEN,
    OISHI_DIR,
    KOJI_DIR,
    ENEMY_DIR,
    HEART_IMG,
)
from player import Player
from enemy import Enemy


def main() -> None:
    """Lance le jeu."""

    # Initialisation
    pygame.init()
    pygame.display.set_caption("47 Ronins Chats – Prototype")

   # Fenêtre et surface de rendu pixelisée
    flags = pygame.FULLSCREEN if FULLSCREEN else 0
    window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), flags)
    canvas = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)).convert()
    clock = pygame.time.Clock()


    # Chemins absolus des assets
    music_path = Path(MUSIC_FILE)
    background_path = Path(BACKGROUND_IMG)

    # Chargement audio + image
    pygame.mixer.music.load(str(music_path))
    pygame.mixer.music.play(-1)

    background = pygame.image.load(str(background_path)).convert()
    background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))

    tileset = pygame.image.load(str(TILESET_IMG)).convert_alpha()
    tile = tileset.subsurface(pygame.Rect(0, 0, 32, 32))
    tile = pygame.transform.scale(tile, (32, 32))

 
    # Entités
    oishi_assets = {
        "stand": OISHI_DIR / "oishi_stand.png",
        "walk": OISHI_DIR / "oishi_walk.png",
        "jump": [
            OISHI_DIR / "Oishi_jump_start.png",
            OISHI_DIR / "Oishi_jump_midair.png",
            OISHI_DIR / "Oishi-jump-landing.png",
        ],
        "sit": OISHI_DIR / "oishi_sit.png",
        "attack": OISHI_DIR / "Oishi-attac.png",
    }

    # L'ancien fichier d'animation de marche de Koji a été supprimé lors d'un
    # nettoyage des assets. Pour éviter une erreur au chargement, on réutilise
    # l'image de base comme animation de marche unique.
    koji_assets = {
        "stand": KOJI_DIR / "Koji_stand.png",
        "walk": KOJI_DIR / "Koji_stand.png",
        "jump": [
            KOJI_DIR / "Koji_jump_start.png",
            KOJI_DIR / "Koji_jump_midair.png",
            KOJI_DIR / "Koji_jump_landing.png",
        ],
        "attack": KOJI_DIR / "Koji_punch.png",
        "kick": KOJI_DIR / "Koji_kick.png",
        "jumpkick": KOJI_DIR / "Koji_jumpkick.png",
    }

    players = [
        Player((WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20), oishi_assets, name="Oishi"),
        Player((WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20), koji_assets, name="Koji"),
    ]
    current_player = 0

    enemy = Enemy((WINDOW_WIDTH - 40, WINDOW_HEIGHT), ENEMY_DIR / "Tengu_stand.png")

    platform = pygame.Rect(WINDOW_WIDTH // 4, WINDOW_HEIGHT - 40, 80, 10)

    heart_img = pygame.image.load(str(HEART_IMG)).convert_alpha()
    heart_scale = int(heart_img.get_width() * 0.012)
    heart = pygame.transform.scale(heart_img, (heart_scale, heart_scale))

    # Boucle principale
    controls = {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "jump": pygame.K_SPACE,
        "attack": pygame.K_f,
        "kick": pygame.K_d,
        "switch": pygame.K_a,
        "down": pygame.K_DOWN,
    }

    menu_open = False
    waiting_key: str | None = None
    music_volume = 1.0
    sfx_volume = 1.0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_open = not menu_open
                elif menu_open and waiting_key is None:
                    if event.key == pygame.K_m:
                        music_volume = max(0.0, music_volume - 0.1)
                        pygame.mixer.music.set_volume(music_volume)
                    elif event.key == pygame.K_p:
                        music_volume = min(1.0, music_volume + 0.1)
                        pygame.mixer.music.set_volume(music_volume)
                    elif event.key == pygame.K_s:
                        sfx_volume = max(0.0, sfx_volume - 0.1)
                    elif event.key == pygame.K_d:
                        sfx_volume = min(1.0, sfx_volume + 0.1)
                    elif event.key == pygame.K_l:
                        waiting_key = "left"
                    elif event.key == pygame.K_r:
                        waiting_key = "right"
                    elif event.key == pygame.K_j:
                        waiting_key = "jump"
                    elif event.key == pygame.K_f:
                        waiting_key = "attack"
                    elif event.key == pygame.K_c:
                        waiting_key = "switch"
                elif menu_open and waiting_key:
                    controls[waiting_key] = event.key
                    waiting_key = None
                elif event.key == controls.get("attack") and not menu_open:
                    players[current_player].start_attack()
                elif event.key == controls.get("kick") and not menu_open:
                    players[current_player].start_kick()
                elif event.key == controls.get("switch") and not menu_open:
                    old = players[current_player]
                    current_player = (current_player + 1) % len(players)
                    players[current_player].hitbox.midbottom = old.hitbox.midbottom

        players[current_player].jump_sound.set_volume(sfx_volume)
        pressed = pygame.key.get_pressed()
        players[current_player].update(pressed, [platform], controls)

        # Gestion des collisions avec l'ennemi
        attack_rect = players[current_player].get_attack_rect()
        enemy_hit = False
        if enemy.health > 0 and attack_rect and enemy.hitbox.colliderect(attack_rect):
            enemy.take_damage(players[current_player].attack_damage())
            enemy_hit = True
        if enemy.health > 0 and players[current_player].hitbox.colliderect(enemy.hitbox) and not enemy_hit:
            players[current_player].take_damage(1)

        canvas.blit(background, (0, 0))
        for x in range(0, WINDOW_WIDTH, tile.get_width()):
            canvas.blit(tile, (x, WINDOW_HEIGHT - tile.get_height()))
        pygame.draw.rect(canvas, (139, 69, 19), platform)
        if enemy.health > 0:
            enemy.draw(canvas)
        players[current_player].draw(canvas)
        players[current_player].draw_health(canvas, heart)

        if menu_open:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            canvas.blit(overlay, (0, 0))
            font = pygame.font.Font(None, 20)
            y = 40
            for line in [
                "Menu - ESC pour fermer",
                "M/P : volume musique",
                "S/D : volume effets",
                "L/R/J/F/C : changer commandes (gauche/droite/saut/attaque/changer)",
                "Touche D : coup de pied",
            ]:
                txt = font.render(line, True, (255, 255, 255))
                canvas.blit(txt, (20, y))
                y += 22
            if waiting_key:
                txt = font.render("Appuyez sur une touche...", True, (255, 255, 0))
                canvas.blit(txt, (20, y))

        pygame.transform.scale(canvas, (DISPLAY_WIDTH, DISPLAY_HEIGHT), window)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
