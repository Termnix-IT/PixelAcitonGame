import pyxel

from .assets import COLKEY, PLAYER_SPRITES, SPRITE_H, SPRITE_W
from .attack import Attack
from .config import (
    PLAYER_ANIM_PERIOD,
    PLAYER_I_FRAME_DURATION,
    PLAYER_MAX_HP,
    SHOOT_COOLDOWN,
)
from .input_handler import InputHandler
from .projectile import Projectile
from .sfx import SFX_ATTACK, SFX_HIT, play_sfx
from .world import World


class Player:
    w = 6
    h = 6
    speed = 1.2

    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.facing: str = "down"
        self.attack: Attack | None = None
        self.projectile: Projectile | None = None
        self._shoot_cd: int = 0
        self.i_frames: int = 0
        self.hp: int = PLAYER_MAX_HP
        self._is_moving: bool = False

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int = 1) -> bool:
        if self.i_frames > 0 or self.hp <= 0:
            return False
        self.hp = max(0, self.hp - amount)
        self.i_frames = PLAYER_I_FRAME_DURATION
        play_sfx(SFX_HIT)
        return True

    def update(self, inp: InputHandler, world: World) -> None:
        if self.i_frames > 0:
            self.i_frames -= 1

        if self.attack is not None:
            self.attack.update()
            if self.attack.is_expired():
                self.attack = None

        if self._shoot_cd > 0:
            self._shoot_cd -= 1

        if self.projectile is not None:
            self.projectile.update(world)
            if self.projectile.is_expired():
                self.projectile = None

        prev_x, prev_y = self.x, self.y
        vx, vy = inp.move_vector()
        self._move_axis(world, vx * self.speed, 0.0)
        self._move_axis(world, 0.0, vy * self.speed)
        self._is_moving = (self.x != prev_x) or (self.y != prev_y)

        # Face the direction of the most recently pressed movement key.
        if inp.is_pressed("move_up"):
            self.facing = "up"
        elif inp.is_pressed("move_down"):
            self.facing = "down"
        elif inp.is_pressed("move_left"):
            self.facing = "left"
        elif inp.is_pressed("move_right"):
            self.facing = "right"

        if inp.is_pressed("attack") and self.attack is None:
            self.attack = Attack.spawn(self.x, self.y, self.w, self.h, self.facing)
            play_sfx(SFX_ATTACK)

        if (
            inp.is_pressed("shoot")
            and self.projectile is None
            and self._shoot_cd <= 0
        ):
            self.projectile = Projectile.spawn(self.x, self.y, self.w, self.h, self.facing)
            self._shoot_cd = SHOOT_COOLDOWN
            play_sfx(SFX_ATTACK)

    def _move_axis(self, world: World, dx: float, dy: float) -> None:
        # Step in <=1px increments so the AABB stops flush against walls.
        sign_x = 1 if dx > 0 else -1 if dx < 0 else 0
        sign_y = 1 if dy > 0 else -1 if dy < 0 else 0
        remaining = abs(dx) + abs(dy)
        while remaining > 1e-6:
            step = 1.0 if remaining >= 1.0 else remaining
            nx = self.x + sign_x * step
            ny = self.y + sign_y * step
            if world.rect_collides(nx, ny, self.w, self.h):
                break
            self.x = nx
            self.y = ny
            remaining -= step

    def draw(self) -> None:
        # Blink every few frames while invulnerable so hits read clearly.
        if self.i_frames > 0 and (self.i_frames // 3) % 2 == 0:
            if self.attack is not None:
                self.attack.draw()
            if self.projectile is not None:
                self.projectile.draw()
            return

        frame = (pyxel.frame_count // PLAYER_ANIM_PERIOD) % 2 if self._is_moving else 0

        if self.facing == "left":
            u, v = PLAYER_SPRITES["right"][frame]
            blt_w = -SPRITE_W
        else:
            u, v = PLAYER_SPRITES[self.facing][frame]
            blt_w = SPRITE_W

        # 8x8 sprite centered on the 6x6 AABB.
        pyxel.blt(int(self.x) - 1, int(self.y) - 1, 0, u, v, blt_w, SPRITE_H, COLKEY)

        if self.attack is not None:
            self.attack.draw()
        if self.projectile is not None:
            self.projectile.draw()
