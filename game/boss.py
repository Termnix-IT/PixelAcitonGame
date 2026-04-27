from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pyxel

from .assets import BOSS_SPRITE, BOSS_SPRITE_H, BOSS_SPRITE_W, COLKEY
from .config import (
    BOSS_FAN_COUNT,
    BOSS_FAN_SPREAD,
    BOSS_FIRE_INTERVAL,
    BOSS_HP,
    BOSS_H,
    BOSS_PHASE_B_BURST_COUNT,
    BOSS_PHASE_B_DASH_INTERVAL,
    BOSS_PHASE_B_DASH_SPEED,
    BOSS_PHASE_B_DASH_TIMEOUT,
    BOSS_PHASE_C_RING_COUNT,
    BOSS_PHASE_C_RING_INTERVAL,
    BOSS_SPEED,
    BOSS_W,
    PROJECTILE_H,
    PROJECTILE_SPEED,
    PROJECTILE_W,
)
from .enemy import Enemy
from .projectile import Projectile
from .sfx import SFX_ATTACK, play_sfx
from .world import World

if TYPE_CHECKING:
    from .player import Player


class Boss(Enemy):
    """Three-phase boss. HP gates the behavior:

    - HP 9–12 (Phase A): drifts toward the player, fan-shoots every BOSS_FIRE_INTERVAL.
    - HP 5–8  (Phase B): periodically dashes at the player; on wall impact, detonates
      into a 4-way burst.
    - HP 1–4  (Phase C): stops moving and emits a 360° ring shot every interval.
    """

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, w=BOSS_W, h=BOSS_H, hp=BOSS_HP)
        self._fire_cd = BOSS_FIRE_INTERVAL
        self._dash_cd = BOSS_PHASE_B_DASH_INTERVAL
        self._ring_cd = BOSS_PHASE_C_RING_INTERVAL
        self._dashing = False
        self._dash_vx = 0.0
        self._dash_vy = 0.0
        self._dash_timer = 0
        self._pending: list[Projectile] = []

    def update(self, world: World, player: "Player") -> None:
        if self.hp >= 9:
            self._phase_a(world, player)
        elif self.hp >= 5:
            self._phase_b(world, player)
        else:
            self._phase_c(player)

    # --- Phase A ------------------------------------------------------------

    def _phase_a(self, world: World, player: "Player") -> None:
        self._drift_toward(world, player, BOSS_SPEED)
        self._fire_cd -= 1
        if self._fire_cd <= 0:
            self._fire_cd = BOSS_FIRE_INTERVAL
            self._fire_fan(player)

    # --- Phase B ------------------------------------------------------------

    def _phase_b(self, world: World, player: "Player") -> None:
        if self._dashing:
            prev_x, prev_y = self.x, self.y
            self._move_axis(world, self._dash_vx, 0.0)
            self._move_axis(world, 0.0, self._dash_vy)
            self._dash_timer -= 1
            # Stop on wall impact (either axis blocked) or on timeout safety net.
            blocked_x = abs(self.x - prev_x) < 1e-6 and self._dash_vx != 0.0
            blocked_y = abs(self.y - prev_y) < 1e-6 and self._dash_vy != 0.0
            if blocked_x or blocked_y or self._dash_timer <= 0:
                self._dashing = False
                self._burst_cardinal()
            return

        # Drift slowly toward the player while waiting to dash.
        self._drift_toward(world, player, BOSS_SPEED * 0.5)
        self._dash_cd -= 1
        if self._dash_cd <= 0:
            self._dash_cd = BOSS_PHASE_B_DASH_INTERVAL
            self._start_dash(player)

    def _start_dash(self, player: "Player") -> None:
        cx = self.x + self.w / 2
        cy = self.y + self.h / 2
        px = player.x + player.w / 2
        py = player.y + player.h / 2
        dx = px - cx
        dy = py - cy
        dist = math.hypot(dx, dy)
        if dist < 1e-6:
            return
        inv = BOSS_PHASE_B_DASH_SPEED / dist
        self._dash_vx = dx * inv
        self._dash_vy = dy * inv
        self._dashing = True
        self._dash_timer = BOSS_PHASE_B_DASH_TIMEOUT
        play_sfx(SFX_ATTACK)

    def _burst_cardinal(self) -> None:
        self._fire_n_way(BOSS_PHASE_B_BURST_COUNT, base_angle=0.0)

    # --- Phase C ------------------------------------------------------------

    def _phase_c(self, player: "Player") -> None:
        # Stationary; punish movement-only avoidance.
        self._ring_cd -= 1
        if self._ring_cd <= 0:
            self._ring_cd = BOSS_PHASE_C_RING_INTERVAL
            self._fire_ring()

    def _fire_ring(self) -> None:
        self._fire_n_way(BOSS_PHASE_C_RING_COUNT, base_angle=0.0)

    # --- shared helpers -----------------------------------------------------

    def _drift_toward(self, world: World, player: "Player", speed: float) -> None:
        cx = self.x + self.w / 2
        cy = self.y + self.h / 2
        px = player.x + player.w / 2
        py = player.y + player.h / 2
        dx = px - cx
        dy = py - cy
        dist_sq = dx * dx + dy * dy
        if dist_sq > 1e-6:
            inv = speed / (dist_sq ** 0.5)
            self._move_axis(world, dx * inv, 0.0)
            self._move_axis(world, 0.0, dy * inv)

    def _fire_fan(self, player: "Player") -> None:
        cx = self.x + self.w / 2
        cy = self.y + self.h / 2
        px = player.x + player.w / 2
        py = player.y + player.h / 2
        base_angle = math.atan2(py - cy, px - cx)
        half = BOSS_FAN_SPREAD / 2
        cx_p = cx - PROJECTILE_W / 2
        cy_p = cy - PROJECTILE_H / 2
        for i in range(BOSS_FAN_COUNT):
            t = i / (BOSS_FAN_COUNT - 1) if BOSS_FAN_COUNT > 1 else 0.5
            angle = base_angle - half + BOSS_FAN_SPREAD * t
            self._pending.append(
                Projectile(
                    cx_p, cy_p,
                    math.cos(angle) * PROJECTILE_SPEED,
                    math.sin(angle) * PROJECTILE_SPEED,
                )
            )
        play_sfx(SFX_ATTACK)

    def _fire_n_way(self, count: int, base_angle: float = 0.0) -> None:
        """Emit `count` projectiles spaced evenly around base_angle (radians)."""
        cx = self.x + self.w / 2 - PROJECTILE_W / 2
        cy = self.y + self.h / 2 - PROJECTILE_H / 2
        for i in range(count):
            angle = base_angle + math.tau * i / count
            self._pending.append(
                Projectile(
                    cx, cy,
                    math.cos(angle) * PROJECTILE_SPEED,
                    math.sin(angle) * PROJECTILE_SPEED,
                )
            )
        play_sfx(SFX_ATTACK)

    def take_pending_projectiles(self) -> list[Projectile]:
        out = self._pending
        self._pending = []
        return out

    def draw(self) -> None:
        u, v = BOSS_SPRITE
        # Pulse the core: swap gold (10) for orange (9) every 12 frames.
        pulsing = (pyxel.frame_count // 12) % 2 == 0
        if pulsing:
            pyxel.pal(10, 9)
        # 16x16 sprite centered on the 12x12 AABB.
        pyxel.blt(int(self.x) - 2, int(self.y) - 2, 0, u, v, BOSS_SPRITE_W, BOSS_SPRITE_H, COLKEY)
        if pulsing:
            pyxel.pal()
