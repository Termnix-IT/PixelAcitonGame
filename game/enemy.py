from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pyxel

from .assets import COLKEY, SLIME_SPRITES, SPRITE_H, SPRITE_W
from .config import (
    COL_ENEMY,
    ENEMY_AGGRO_DIST,
    ENEMY_CHASE_SPEED,
    ENEMY_WANDER_SPEED,
    ENEMY_WANDER_TICKS,
    SLIME_ANIM_PERIOD,
)
from .world import World

if TYPE_CHECKING:
    from .player import Player


class Enemy:
    def __init__(self, x: float, y: float, w: int = 6, h: int = 6, hp: int = 1) -> None:
        self.x = float(x)
        self.y = float(y)
        self.w = w
        self.h = h
        self.hp = hp
        self.alive = True

    def update(self, world: World, player: "Player") -> None:
        pass

    def draw(self) -> None:
        pyxel.rect(int(self.x), int(self.y), self.w, self.h, COL_ENEMY)

    def rect_overlaps(self, x: float, y: float, w: int, h: int) -> bool:
        return (
            self.x < x + w
            and x < self.x + self.w
            and self.y < y + h
            and y < self.y + self.h
        )

    def _move_axis(self, world: World, dx: float, dy: float) -> None:
        sign_x = 1 if dx > 0 else -1 if dx < 0 else 0
        sign_y = 1 if dy > 0 else -1 if dy < 0 else 0
        remaining = abs(dx) + abs(dy)
        while remaining > 1e-6:
            step = 1.0 if remaining >= 1.0 else remaining
            nx = self.x + sign_x * step
            ny = self.y + sign_y * step
            if world.rect_collides(nx, ny, self.w, self.h):
                return
            self.x = nx
            self.y = ny
            remaining -= step


class Slime(Enemy):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, w=6, h=6, hp=2)
        self._wander_dx = 0.0
        self._wander_dy = 0.0
        self._wander_ticks = 0
        self._aggro = False

    def update(self, world: World, player: "Player") -> None:
        cx = self.x + self.w / 2
        cy = self.y + self.h / 2
        px = player.x + player.w / 2
        py = player.y + player.h / 2
        dx = px - cx
        dy = py - cy
        dist_sq = dx * dx + dy * dy
        self._aggro = dist_sq < ENEMY_AGGRO_DIST * ENEMY_AGGRO_DIST

        if self._aggro and dist_sq > 1e-6:
            dist = dist_sq ** 0.5
            inv = ENEMY_CHASE_SPEED / dist
            vx = dx * inv
            vy = dy * inv
        else:
            if self._wander_ticks <= 0:
                self._reroll_wander(world)
            self._wander_ticks -= 1
            vx = self._wander_dx
            vy = self._wander_dy

        self._move_axis(world, vx, 0.0)
        self._move_axis(world, 0.0, vy)

    def _reroll_wander(self, world: World) -> None:
        dirs = (
            (0, 0),
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1),
        )
        dx_c, dy_c = random.choice(dirs)
        mag = (dx_c * dx_c + dy_c * dy_c) ** 0.5
        if mag > 0:
            self._wander_dx = dx_c / mag * ENEMY_WANDER_SPEED
            self._wander_dy = dy_c / mag * ENEMY_WANDER_SPEED
        else:
            self._wander_dx = 0.0
            self._wander_dy = 0.0
        self._wander_ticks = ENEMY_WANDER_TICKS

    def draw(self) -> None:
        frame = (pyxel.frame_count // SLIME_ANIM_PERIOD) % 2
        u, v = SLIME_SPRITES[frame]
        if self._aggro:
            pyxel.pal(14, 8)
        pyxel.blt(int(self.x) - 1, int(self.y) - 1, 0, u, v, SPRITE_W, SPRITE_H, COLKEY)
        if self._aggro:
            pyxel.pal()
