"""settings.py
Définit toutes les constantes de configuration du jeu : dimensions d’écran, couleurs, physique, etc.
Ce fichier centralise les paramètres pour simplifier les ajustements ultérieurs.
"""

from pathlib import Path

# —— Dimensions d’origine (pixel‑art) ——
WINDOW_WIDTH: int = 320
WINDOW_HEIGHT: int = 240
# Augmente le facteur de mise à l'échelle pour une résolution plus élevée.
UPSCALE: int = 4  # 320×240 → 1280×960

DISPLAY_WIDTH: int = WINDOW_WIDTH * UPSCALE
DISPLAY_HEIGHT: int = WINDOW_HEIGHT * UPSCALE

# —— Couleurs ——
SKY_BLUE: tuple[int, int, int] = (92, 148, 252)  # Fond provisoire
PLAYER_RED: tuple[int, int, int] = (222, 68, 55)

# Taille du joueur (facteur de réduction des sprites d'origine)
PLAYER_SCALE: float = 0.0625  # 1024px -> 64px environ

# Mode plein écran
FULLSCREEN: bool = False

# —— Physique du joueur ——
FPS: int = 60
PLAYER_SPEED: float = 2.5  # Vitesse horizontale en px par frame (avant upscale)
GRAVITY: float = 0.35      # Accélération gravitationnelle
JUMP_SPEED: float = -6.5   # Impulsion verticale du saut (négatif = vers le haut)
LANDING_TIME: int = 6      # Durée d'affichage de la frame d'atterrissage

# —— Autres ——
GROUND_Y: int = WINDOW_HEIGHT  # Limite inférieure (sol) pour collision simple

# —— Assets ——
BASE_DIR: Path = Path(__file__).resolve().parent.parent
ASSETS_DIR: Path = BASE_DIR / "assets"

# Arrière-plan principal du stage.  On réutilise l'image
# ``background_forest.png`` provenant du dossier ``assets/niveaux`` afin de
# centraliser tous les décors dans le répertoire des assets.
BACKGROUND_IMG: Path = ASSETS_DIR / "niveaux" / "background_forest.png"
BACKGROUND_IMG_2: Path = ASSETS_DIR / "niveaux" / "background_forest2.png"
TILESET_IMG: Path = ASSETS_DIR / "niveaux" / "tileset_forest.png"
PLATFORM_TILESET_IMG: Path = ASSETS_DIR / "niveaux" / "tileset_plateform_1.png"
MUSIC_FILE: Path = ASSETS_DIR / "son" / "music_stage_1.wav"
JUMP_SOUND_FILE: Path = ASSETS_DIR / "son" / "son_saut.wav"
PUNCH_SOUND_FILE: Path = ASSETS_DIR / "son" / "punch1.wav"
KICK_SOUND_FILE: Path = ASSETS_DIR / "son" / "kick1.wav"
SWORD_SOUND_FILE: Path = ASSETS_DIR / "son" / "sword-attac1.wav"
# Le fichier "tengu_hurt.wma" a été remplacé par "Tengu_hurt.wav" dans les assets.
# On met à jour le chemin pour éviter une erreur de chargement.
TENGU_HURT_FILE: Path = ASSETS_DIR / "son" / "Tengu_hurt.wav"

CHARACTER_DIR: Path = ASSETS_DIR / "personnages"
OISHI_DIR: Path = CHARACTER_DIR / "1_Oishi_Samourai"
KOJI_DIR: Path = CHARACTER_DIR / "2_Koji_Karateka"
ENEMY_DIR: Path = ASSETS_DIR / "ennemis"

HEART_IMG: Path = ASSETS_DIR / "ui" / "Heart_lifepoint.png"
SNES_IMG: Path = ASSETS_DIR / "ui" / "Manette_SNES.png"


