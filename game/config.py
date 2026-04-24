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

# Player visual / action tuning
PLAYER_ANIM_PERIOD = 8        # frames per walk-cycle pattern
PLAYER_MAX_HP = 3
PLAYER_I_FRAME_DURATION = 48  # frames of invulnerability after taking a hit
ATTACK_DURATION = 6           # frames the hitbox stays visible/active
ATTACK_REACH = 6              # pixels the hitbox extends in the facing direction

# Enemy tuning
ENEMY_WANDER_SPEED = 0.35
ENEMY_CHASE_SPEED = 0.8
ENEMY_AGGRO_DIST = 40         # pixels — straight-line distance to switch into chase
ENEMY_WANDER_TICKS = 45       # frames between picking a new wander direction
ENEMY_KILL_SHAKE_FRAMES = 4   # how long the screen jitters after a kill
SLIME_ANIM_PERIOD = 12        # slime idle/move breathing rate

KEYBINDS: dict[str, list[int]] = {
    "move_up":    [pyxel.KEY_UP, pyxel.KEY_W],
    "move_down":  [pyxel.KEY_DOWN, pyxel.KEY_S],
    "move_left":  [pyxel.KEY_LEFT, pyxel.KEY_A],
    "move_right": [pyxel.KEY_RIGHT, pyxel.KEY_D],
    "confirm":    [pyxel.KEY_SPACE, pyxel.KEY_RETURN],
    "back":       [pyxel.KEY_ESCAPE],
    "attack":     [pyxel.KEY_Z],
}
