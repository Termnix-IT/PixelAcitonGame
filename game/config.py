import pyxel

SCREEN_W = 192
SCREEN_H = 128
FPS = 60
TITLE = "Pixel Action"

TILE_SIZE = 8
STAGE_W = 48
STAGE_H = 32

COL_BG = 0
COL_ATTACK = 10
COL_ENEMY = 8
COL_HP = 8
COL_HP_EMPTY = 13
COL_TEXT = 7
COL_TEXT_DIM = 13
COL_BOSS_CORE = 10            # the gold "drop" core inside the boss
COL_KEY_ICON = 10             # HUD key indicator color

# Player visual / action tuning
PLAYER_ANIM_PERIOD = 8        # frames per walk-cycle pattern
PLAYER_MAX_HP = 3
PLAYER_I_FRAME_DURATION = 48  # frames of invulnerability after taking a hit
ATTACK_DURATION = 6           # frames the hitbox stays visible/active
ATTACK_REACH = 6              # pixels the hitbox extends in the facing direction

# Ranged attack tuning
PROJECTILE_W = 2
PROJECTILE_H = 2
PROJECTILE_SPEED = 2.0        # pixels per frame, faster than the player to feel sharp
PROJECTILE_MAX_LIFE = 60      # frames before auto-expiry (safety net)
SHOOT_COOLDOWN = 24           # frames the player must wait between shots

# Enemy tuning
ENEMY_WANDER_SPEED = 0.35
ENEMY_CHASE_SPEED = 0.8
ENEMY_AGGRO_DIST = 40         # pixels — straight-line distance to switch into chase
ENEMY_WANDER_TICKS = 45       # frames between picking a new wander direction
ENEMY_KILL_SHAKE_FRAMES = 4   # how long the screen jitters after a kill
SLIME_ANIM_PERIOD = 12        # slime idle/move breathing rate

# DashSlime — short bursts of high-speed movement while aggro'd
DASH_SLIME_HP = 2
DASH_INTERVAL = 90            # frames between dashes
DASH_DURATION = 20            # frames spent in dash
DASH_SPEED_MUL = 2.5

# TankSlime — fat, slow, drops a key when killed (used in stage 4)
TANK_SLIME_HP = 5
TANK_SLIME_SPEED_MUL = 0.5
TANK_SLIME_W = 12
TANK_SLIME_H = 12

# Boss "THE CORE" — final-room enemy
BOSS_HP = 12
BOSS_W = 12
BOSS_H = 12
BOSS_SPEED = 0.4              # gentle oscillation in the boss room
BOSS_FIRE_INTERVAL = 120      # frames between fan-shot volleys
BOSS_FAN_COUNT = 5            # bullets per volley
BOSS_FAN_SPREAD = 0.6         # radians: total spread of the fan
BOSS_KILL_SHAKE_FRAMES = 30
BOSS_KILL_BURST_COUNT = 40
# Phase B (HP 8–5): high-speed dashes that detonate on wall impact
BOSS_PHASE_B_DASH_INTERVAL = 90
BOSS_PHASE_B_DASH_SPEED = 1.8
BOSS_PHASE_B_DASH_TIMEOUT = 60  # safety cap so dashes always end in a burst
BOSS_PHASE_B_BURST_COUNT = 4   # bullets fired in cardinal dirs on wall impact
# Phase C (HP 4–0): stationary; periodic ring shots
BOSS_PHASE_C_RING_INTERVAL = 120
BOSS_PHASE_C_RING_COUNT = 12   # bullets per ring (every 30°)

# RangedSlime — paper-thin, fires aimed shots while aggro'd
RANGED_SLIME_HP = 1
RANGED_FIRE_INTERVAL = 90

# Player level system — driven by score, lifts ranged damage
LEVEL_THRESHOLDS = (0, 500, 1500)    # score thresholds: Lv1, Lv2, Lv3
LEVEL_DAMAGES = (1, 2, 3)            # ranged damage per level
LEVEL_UP_DISPLAY_FRAMES = 60         # frames the "LEVEL UP!" banner stays up

KEYBINDS: dict[str, list[int]] = {
    "move_up":    [pyxel.KEY_UP, pyxel.KEY_W],
    "move_down":  [pyxel.KEY_DOWN, pyxel.KEY_S],
    "move_left":  [pyxel.KEY_LEFT, pyxel.KEY_A],
    "move_right": [pyxel.KEY_RIGHT, pyxel.KEY_D],
    "confirm":    [pyxel.KEY_SPACE, pyxel.KEY_RETURN],
    "back":       [pyxel.KEY_ESCAPE],
    "attack":     [pyxel.KEY_Z],
    "shoot":      [pyxel.KEY_X],
}
