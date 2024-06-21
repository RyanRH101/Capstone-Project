# Game Settings

import pygame as pg
vec = pg.math.Vector2

# define colorus (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARKGRAY = (40, 40, 40)
LIGHTGRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
CYAN = (0, 255, 255)

MAP_WIDTH = 2048
MAP_HEIGHT = 768
TILE_SIZE = 16

# Game display width and height in pixels:
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 768

MAP_WIDTH = 2048
MAP_HEIGHT = 768

# Game display width and height in tiles:
GRID_WIDTH = DISPLAY_WIDTH / TILE_SIZE
GRID_HEIGHT = DISPLAY_HEIGHT / TILE_SIZE

# Desired number of FPS for game:
DESIRED_FPS = 60

BACKGROUND_COLOUR = CYAN

# The following will be removed/replaced:
WALL_IMG = 'tileGreen_39.png'

# Player settings
PLAYER_IMG = 'monkey2.png'
PLAYER_HIT_RECT = pg.Rect(0, 0, 21, 30)
PLAYER_LIVES = 3
PLAYER_SPEED = 250

PLAYER_INITIAL_JUMP_HEIGHT = 100
PLAYER_JUMP_SPEED = -500
GRAVITY_INITIAL_DOWN_SPEED = 300
GRAVITY_INCREMENT = 15
GRAVITY_UP_INCREMENT = 15

# Fire settings for player
BULLET_IMG = 'Bullet-4x4.png'
BULLET_SPEED = 400
BULLET_LIFETIME = 2500
BULLET_RATE = 150
BULLET_MAX_ACTIVE = 5
BARREL_OFFSET_RIGHT = vec(12, 6)
BARREL_OFFSET_LEFT = vec(-1, 6)

# Points earned for each enemy and guard killed and also for each new level:
POINTS_ENEMY = 50
POINTS_GUARD = 30
POINTS_ENEMY_BONUS = 150
POINTS_GUARD_BONUS = 100
POINTS_LEVEL_BONUS = 200
# player earns a new life every 1000 points earned:
SCORE_NEW_LIFE = 1000

ENEMY_BULLET_IMG = 'EnemyBullet-4x4.png'
ENEMY_BULLET_SPEED = 250
ENEMY_BULLET_LIFETIME = 2000
ENEMY_BULLET_RATE = 1500

# The following is for platform guards as well as 
PLATFORM_GUARD_IMG = 'green.gif'
ENEMY_IMG = 'blue.gif'
ENEMY_ROTATION_SPEED_MIN = 50
ENEMY_ROTATION_SPEED_MAX = 500
ENEMY_MOVEMENT_SPEED_MIN = 50
ENEMY_MOVEMENT_SPEED_MAX = 80
ENEMY_MINIMUM_FIRE_DISTANCE_TO_PLAYER = TILE_SIZE * 15 #10
ENEMY_MINIMUM_MOVE_DISTANCE_TOWARDS_PLAYER = TILE_SIZE * 20 #15

# Sound effects
SOUND_PLAYER_GUNSHOT = "mixkit-game-gun-shot-1662_trimmed.wav"
SOUND_PLAYER_HIT = "mixkit-player-losing-or-failing-2042_trimmed.wav"
SOUND_ENEMY_GUNSHOT = "mixkit-arrow-shot-through-air-2771_trimmed.wav"
SOUND_ENEMY_HIT = "mixkit-small-hit-in-a-game-2072_trimmed.wav"
SOUND_LIFE_EARNED = "mixkit-bonus-earned-in-video-game-2058_trimmed.wav"
SOUND_LEVEL_COMPLETE = "mixkit-completion-of-a-level-2063_trimmed.wav"
SOUND_ENEMY_GUNSHOT = "mixkit-arrow-shot-through-air-2771_trimmed.wav"
SOUND_ENEMY_CRUSHED = "mixkit-creature-cry-of-hurt-2208_trimmed.wav"

# Layers
WALL_LAYER = 1
GROUND_LAYER = 1
PLAYER_LAYER = 2
BULLET_LAYER = 3
ENEMY_LAYER = 2
