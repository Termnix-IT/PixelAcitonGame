import pyxel

from .config import (
    COL_ATTACK,
    PROJECTILE_H,
    PROJECTILE_MAX_LIFE,
    PROJECTILE_SPEED,
    PROJECTILE_W,
)
from .world import World


class Projectile:
    def __init__(self, x: float, y: float, vx: float, vy: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.w = PROJECTILE_W
        self.h = PROJECTILE_H
        self._life = PROJECTILE_MAX_LIFE
        self._hit_wall = False

    @classmethod
    def spawn(cls, px: float, py: float, pw: int, ph: int, facing: str) -> "Projectile":
        # Spawn centered on the player, just past the AABB edge in the facing direction.
        cx = px + pw / 2 - PROJECTILE_W / 2
        cy = py + ph / 2 - PROJECTILE_H / 2
        if facing == "up":
            return cls(cx, py - PROJECTILE_H, 0.0, -PROJECTILE_SPEED)
        if facing == "down":
            return cls(cx, py + ph, 0.0, PROJECTILE_SPEED)
        if facing == "left":
            return cls(px - PROJECTILE_W, cy, -PROJECTILE_SPEED, 0.0)
        return cls(px + pw, cy, PROJECTILE_SPEED, 0.0)

    def update(self, world: World) -> None:
        self.x += self.vx
        self.y += self.vy
        self._life -= 1
        if world.rect_collides(self.x, self.y, self.w, self.h):
            self._hit_wall = True

    def is_expired(self) -> bool:
        return self._life <= 0 or self._hit_wall

    def expire(self) -> None:
        self._hit_wall = True

    def rect_overlaps(self, x: float, y: float, w: int, h: int) -> bool:
        return (
            self.x < x + w
            and x < self.x + self.w
            and self.y < y + h
            and y < self.y + self.h
        )

    def draw(self) -> None:
        pyxel.rect(int(self.x), int(self.y), self.w, self.h, COL_ATTACK)
