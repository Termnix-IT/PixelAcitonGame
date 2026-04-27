from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

import pyxel

from .assets import (
    COLKEY,
    SLIME_SPRITES,
    SPRITE_H,
    SPRITE_W,
    TANK_SPRITES,
    TANK_SPRITE_H,
    TANK_SPRITE_W,
)
from .config import (
    COL_ENEMY,
    DASH_DURATION,
    DASH_INTERVAL,
    DASH_SLIME_HP,
    DASH_SPEED_MUL,
    ENEMY_AGGRO_DIST,
    ENEMY_CHASE_SPEED,
    ENEMY_WANDER_SPEED,
    ENEMY_WANDER_TICKS,
    PROJECTILE_H,
    PROJECTILE_SPEED,
    PROJECTILE_W,
    RANGED_FIRE_INTERVAL,
    RANGED_SLIME_HP,
    SLIME_ANIM_PERIOD,
    TANK_SLIME_HP,
    TANK_SLIME_H,
    TANK_SLIME_SPEED_MUL,
    TANK_SLIME_W,
)
from .projectile import Projectile
from .world import World

if TYPE_CHECKING:
    from .player import Player


class Enemy:
    contact_damage: int = 1

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


class DashSlime(Slime):
    """Slime that periodically lunges at the player when aggro'd."""

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y)
        self.hp = DASH_SLIME_HP
        self._dash_cd = DASH_INTERVAL
        self._dash_remain = 0
        self._dash_vx = 0.0
        self._dash_vy = 0.0

    def update(self, world: World, player: "Player") -> None:
        cx = self.x + self.w / 2
        cy = self.y + self.h / 2
        px = player.x + player.w / 2
        py = player.y + player.h / 2
        dx = px - cx
        dy = py - cy
        dist_sq = dx * dx + dy * dy
        self._aggro = dist_sq < ENEMY_AGGRO_DIST * ENEMY_AGGRO_DIST

        if self._dash_remain > 0:
            self._dash_remain -= 1
            self._move_axis(world, self._dash_vx, 0.0)
            self._move_axis(world, 0.0, self._dash_vy)
            return

        if self._aggro:
            self._dash_cd -= 1
            if self._dash_cd <= 0 and dist_sq > 1e-6:
                inv = (ENEMY_CHASE_SPEED * DASH_SPEED_MUL) / (dist_sq ** 0.5)
                self._dash_vx = dx * inv
                self._dash_vy = dy * inv
                self._dash_remain = DASH_DURATION
                self._dash_cd = DASH_INTERVAL
                return
            super().update(world, player)
        else:
            super().update(world, player)

    def draw(self) -> None:
        frame = (pyxel.frame_count // SLIME_ANIM_PERIOD) % 2
        u, v = SLIME_SPRITES[frame]
        if self._dash_remain > 0:
            pyxel.pal(14, 11)
        elif self._aggro:
            pyxel.pal(14, 8)
        pyxel.blt(int(self.x) - 1, int(self.y) - 1, 0, u, v, SPRITE_W, SPRITE_H, COLKEY)
        if self._aggro or self._dash_remain > 0:
            pyxel.pal()


class TankSlime(Slime):
    """Slow, fat slime with high HP and double contact damage. Drops a key on death."""

    contact_damage: int = 2

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y)
        self.w = TANK_SLIME_W
        self.h = TANK_SLIME_H
        self.hp = TANK_SLIME_HP

    def update(self, world: World, player: "Player") -> None:
        cx = self.x + self.w / 2
        cy = self.y + self.h / 2
        px = player.x + player.w / 2
        py = player.y + player.h / 2
        dx = px - cx
        dy = py - cy
        dist_sq = dx * dx + dy * dy
        self._aggro = dist_sq < (ENEMY_AGGRO_DIST * 1.5) ** 2

        if self._aggro and dist_sq > 1e-6:
            inv = (ENEMY_CHASE_SPEED * TANK_SLIME_SPEED_MUL) / (dist_sq ** 0.5)
            vx = dx * inv
            vy = dy * inv
        else:
            if self._wander_ticks <= 0:
                self._reroll_wander(world)
            self._wander_ticks -= 1
            vx = self._wander_dx * TANK_SLIME_SPEED_MUL
            vy = self._wander_dy * TANK_SLIME_SPEED_MUL

        self._move_axis(world, vx, 0.0)
        self._move_axis(world, 0.0, vy)

    def draw(self) -> None:
        frame = (pyxel.frame_count // SLIME_ANIM_PERIOD) % 2
        u, v = TANK_SPRITES[frame]
        # 12x12 sprite centered on the 8x8 AABB so the silhouette overhangs the
        # tighter collision box.
        ox = (TANK_SPRITE_W - self.w) // 2
        oy = (TANK_SPRITE_H - self.h) // 2
        pyxel.blt(int(self.x) - ox, int(self.y) - oy, 0, u, v, TANK_SPRITE_W, TANK_SPRITE_H, COLKEY)


class RangedSlime(Slime):
    """Paper-thin slime that fires aimed shots while aggro'd.

    Movement reuses the standard Slime wander/chase. When aggro'd, fires a single
    Projectile toward the player every RANGED_FIRE_INTERVAL frames. The PlayScene
    drains pending shots into its enemy_projectiles pool each tick.
    """

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y)
        self.hp = RANGED_SLIME_HP
        self._fire_cd = RANGED_FIRE_INTERVAL
        self._pending: list[Projectile] = []

    def update(self, world: World, player: "Player") -> None:
        super().update(world, player)
        if self._aggro:
            self._fire_cd -= 1
            if self._fire_cd <= 0:
                self._fire_cd = RANGED_FIRE_INTERVAL
                self._fire_at(player)

    def _fire_at(self, player: "Player") -> None:
        cx = self.x + self.w / 2
        cy = self.y + self.h / 2
        px = player.x + player.w / 2
        py = player.y + player.h / 2
        dx = px - cx
        dy = py - cy
        dist = math.hypot(dx, dy)
        if dist < 1e-6:
            return
        inv = PROJECTILE_SPEED / dist
        self._pending.append(
            Projectile(cx - PROJECTILE_W / 2, cy - PROJECTILE_H / 2, dx * inv, dy * inv)
        )

    def take_pending_projectiles(self) -> list[Projectile]:
        out = self._pending
        self._pending = []
        return out

    def draw(self) -> None:
        frame = (pyxel.frame_count // SLIME_ANIM_PERIOD) % 2
        u, v = SLIME_SPRITES[frame]
        # Always tinted green so the player can read "this one shoots" at a glance.
        pyxel.pal(14, 11)
        pyxel.blt(int(self.x) - 1, int(self.y) - 1, 0, u, v, SPRITE_W, SPRITE_H, COLKEY)
        pyxel.pal()
