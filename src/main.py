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
    BACKGROUND_IMG_2,
    TILESET_IMG,
    MUSIC_FILE,
    PUNCH_SOUND_FILE,
    KICK_SOUND_FILE,
    SWORD_SOUND_FILE,
    TENGU_HURT_FILE,
    FULLSCREEN,
    OISHI_DIR,
    KOJI_DIR,
    ENEMY_DIR,
    HEART_IMG,
    SNES_IMG,
)
from player import Player
from enemy import Enemy
from platforms import create_level_platforms, create_level_ladders


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
    background2_path = Path(BACKGROUND_IMG_2)

    # Chargement audio + image
    pygame.mixer.music.load(str(music_path))
    pygame.mixer.music.play(-1)

    # effets sonores
    punch_snd = pygame.mixer.Sound(str(PUNCH_SOUND_FILE))
    kick_snd = pygame.mixer.Sound(str(KICK_SOUND_FILE))
    sword_snd = pygame.mixer.Sound(str(SWORD_SOUND_FILE))
    tengu_hurt_snd = pygame.mixer.Sound(str(TENGU_HURT_FILE))

    background = pygame.image.load(str(background_path)).convert()
    background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
    background2 = pygame.image.load(str(background2_path)).convert()
    background2 = pygame.transform.scale(background2, (WINDOW_WIDTH, WINDOW_HEIGHT))

    platforms = create_level_platforms()
    ladders = create_level_ladders(platforms)

    level_width = WINDOW_WIDTH * 2

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
        "hurt": OISHI_DIR / "Oishi_hurt.png",
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
        "kick": KOJI_DIR / "Koji_attac2_kick.png",
        "jumpkick": KOJI_DIR / "Koji_jumpkick.png",
        "hurt": KOJI_DIR / "Koji_hurt.png",
    }

    players = [
        Player((40, WINDOW_HEIGHT - 20), oishi_assets, name="Oishi"),
        Player((40, WINDOW_HEIGHT - 20), koji_assets, name="Koji"),
    ]
    current_player = 0

    enemy = Enemy(
        (WINDOW_WIDTH // 2, WINDOW_HEIGHT),
        ENEMY_DIR / "Tengu_stand_left.png",
        ENEMY_DIR / "Tengu_attac.png",
        patrol_left=WINDOW_WIDTH // 2 - 40,
        patrol_right=WINDOW_WIDTH // 2 + 40,
    )

    # Second Tengu placed on the third platform
    plat = platforms[-1]
    enemy2 = Enemy(
        (plat.rect.centerx, plat.rect.top),
        ENEMY_DIR / "Tengu_stand_left.png",
        ENEMY_DIR / "Tengu_attac.png",
        patrol_left=plat.rect.left,
        patrol_right=plat.rect.right,
    )
    enemies = [enemy, enemy2]

    heart_img = pygame.image.load(str(HEART_IMG)).convert_alpha()
    heart_scale = int(heart_img.get_width() * 0.012)
    heart = pygame.transform.scale(heart_img, (heart_scale, heart_scale))

    # Boucle principale
    controls = {
        "up": pygame.K_UP,
        "down": pygame.K_DOWN,
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "attack": pygame.K_d,  # A
        "kick": pygame.K_f,    # B
        "special": pygame.K_s,  # X
        "jump": pygame.K_SPACE,  # Y
        "next": pygame.K_e,   # R
        "prev": pygame.K_r,   # L
    }
    keys = [
        "up",
        "down",
        "left",
        "right",
        "attack",
        "kick",
        "special",
        "jump",
        "prev",
        "next",
    ]

    menu_open = False
    waiting_key: str | None = None
    selected_key = 0
    music_volume = 1.0
    sfx_volume = 1.0

    camera_x = 0
    running = True
    game_over = False
    restart = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_o:
                        restart = True
                        running = False
                    continue
                if event.key == pygame.K_ESCAPE:
                    menu_open = not menu_open
                    if menu_open:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
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
                    elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                        cols = 5
                        row = selected_key // cols
                        col = selected_key % cols
                        if event.key == pygame.K_LEFT and col > 0:
                            col -= 1
                        elif event.key == pygame.K_RIGHT and col < cols - 1 and row * cols + col + 1 < len(keys):
                            col += 1
                        elif event.key == pygame.K_UP and row > 0:
                            row -= 1
                        elif event.key == pygame.K_DOWN and (row + 1) * cols + col < len(keys):
                            row += 1
                        selected_key = row * cols + col
                    elif event.key == pygame.K_RETURN:
                        waiting_key = keys[selected_key]
                elif menu_open and waiting_key:
                    controls[waiting_key] = event.key
                    waiting_key = None
                elif event.key == controls.get("attack") and not menu_open:
                    players[current_player].start_attack()
                    if players[current_player].name.lower() == "oishi":
                        sword_snd.set_volume(sfx_volume)
                        sword_snd.play()
                elif event.key == controls.get("kick") and not menu_open:
                    players[current_player].start_kick()
                elif event.key == controls.get("next") and not menu_open:
                    old = players[current_player]
                    current_player = (current_player + 1) % len(players)
                    players[current_player].hitbox.midbottom = old.hitbox.midbottom
                elif event.key == controls.get("prev") and not menu_open:
                    old = players[current_player]
                    current_player = (current_player - 1) % len(players)
                    players[current_player].hitbox.midbottom = old.hitbox.midbottom
                elif event.key == pygame.K_p and not menu_open:
                    restart = True
                    running = False

        if not game_over:
            players[current_player].jump_sound.set_volume(sfx_volume)
            pressed = pygame.key.get_pressed()
            players[current_player].update(
                pressed,
                [p.rect for p in platforms],
                [l.rect for l in ladders],
                controls,
            )
            camera_x = max(0, min(level_width - WINDOW_WIDTH, players[current_player].hitbox.centerx - WINDOW_WIDTH // 2))
            attack_rect = players[current_player].get_attack_rect()
            for en in enemies:
                # trouve le joueur le plus proche pour orienter le Tengu
                target = min(players, key=lambda p: abs(p.hitbox.centerx - en.hitbox.centerx))
                en.update(target.hitbox)

                enemy_hit = False
                if en.health > 0 and attack_rect and en.hitbox.colliderect(attack_rect):
                    en.take_damage(players[current_player].attack_damage())
                    enemy_hit = True
                    if players[current_player].attack_type == "kick":
                        snd = kick_snd
                    else:
                        snd = punch_snd
                    snd.set_volume(sfx_volume)
                    snd.play()
                    tengu_hurt_snd.set_volume(sfx_volume)
                    tengu_hurt_snd.play()
                enemy_attack = en.get_attack_rect()
                if (
                    en.health > 0
                    and enemy_attack
                    and enemy_attack.colliderect(players[current_player].hitbox)
                ):
                    from_left = enemy_attack.centerx < players[current_player].hitbox.centerx
                    players[current_player].take_damage(1, from_left)
                elif en.health > 0 and players[current_player].hitbox.colliderect(en.hitbox) and not enemy_hit:
                    from_left = en.hitbox.centerx < players[current_player].hitbox.centerx
                    players[current_player].take_damage(1, from_left)

            # Switch character if health depleted
            if players[current_player].health <= 0:
                next_idx = None
                for i in range(len(players)):
                    idx = (current_player + i + 1) % len(players)
                    if players[idx].health > 0:
                        next_idx = idx
                        break
                if next_idx is not None:
                    players[next_idx].hitbox.midbottom = players[current_player].hitbox.midbottom
                    current_player = next_idx
                else:
                    game_over = True

        canvas.blit(background, (-camera_x, 0))
        canvas.blit(background2, (WINDOW_WIDTH - camera_x, 0))
        for x in range(0, level_width, tile.get_width()):
            canvas.blit(tile, (x - camera_x, WINDOW_HEIGHT - tile.get_height()))
        for plat in platforms:
            canvas.blit(plat.image, (plat.rect.x - camera_x, plat.rect.y))
        for lad in ladders:
            canvas.blit(lad.image, (lad.rect.x - camera_x, lad.rect.y))
        for en in enemies:
            if en.health > 0:
                en.draw(canvas, camera_x)
        players[current_player].draw(canvas, camera_x)
        players[current_player].draw_health(canvas, heart)

        if game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            canvas.blit(overlay, (0, 0))
            font = pygame.font.Font(None, 32)
            msg = font.render("Game Over - Press 'O' to restart", True, (255, 255, 255))
            rect = msg.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            canvas.blit(msg, rect)

        if menu_open:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            canvas.blit(overlay, (0, 0))
            font = pygame.font.Font(None, 24)
            title = font.render("Menu", True, (255, 255, 255))
            canvas.blit(title, (20, 20))

            # Sliders volume
            bar_w = 100
            bar_h = 6
            vol_y = 50
            pygame.draw.rect(canvas, (100, 100, 100), (20, vol_y, bar_w, bar_h))
            pygame.draw.rect(canvas, (255, 255, 255), (20, vol_y, int(bar_w * music_volume), bar_h))
            txt = font.render("Musique", True, (255, 255, 255))
            canvas.blit(txt, (130, vol_y - 4))

            vol_y += 20
            pygame.draw.rect(canvas, (100, 100, 100), (20, vol_y, bar_w, bar_h))
            pygame.draw.rect(canvas, (255, 255, 255), (20, vol_y, int(bar_w * sfx_volume), bar_h))
            txt = font.render("Effets", True, (255, 255, 255))
            canvas.blit(txt, (130, vol_y - 4))

            snes = pygame.image.load(str(SNES_IMG)).convert_alpha()
            snes = pygame.transform.scale(snes, (120, 60))
            canvas.blit(snes, (20, vol_y + 30))

            key_y = vol_y + 100
            box_w = 20
            for i, k in enumerate(keys):
                x = 20 + (i % 5) * 60
                y = key_y + (i // 5) * 30
                color = (255, 0, 0) if i == selected_key else (200, 200, 200)
                pygame.draw.rect(canvas, color, (x, y, box_w, box_w), 1)
                name = pygame.key.name(controls[k])
                txt = font.render(name, True, (255, 255, 255))
                canvas.blit(txt, (x + box_w + 4, y))

            if waiting_key:
                txt = font.render("Appuyez sur une touche...", True, (255, 255, 0))
                canvas.blit(txt, (20, key_y + 70))

        pygame.transform.scale(canvas, (DISPLAY_WIDTH, DISPLAY_HEIGHT), window)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    if restart:
        main()
        return
    sys.exit()


if __name__ == "__main__":
    main()
