import pyxel

from .config import ATTACK_DURATION, ATTACK_REACH, COL_ATTACK


class Attack:
    def __init__(self, x: float, y: float, w: int, h: int) -> None:
        self.x = float(x)
        self.y = float(y)
        self.w = w
        self.h = h
        self._life = ATTACK_DURATION

    @classmethod
    def spawn(cls, px: float, py: float, pw: int, ph: int, facing: str) -> "Attack":
        if facing == "up":
            return cls(px, py - ATTACK_REACH, pw, ATTACK_REACH)
        if facing == "down":
            return cls(px, py + ph, pw, ATTACK_REACH)
        if facing == "left":
            return cls(px - ATTACK_REACH, py, ATTACK_REACH, ph)
        return cls(px + pw, py, ATTACK_REACH, ph)

    def update(self) -> None:
        self._life -= 1

    def is_expired(self) -> bool:
        return self._life <= 0

    def rect_overlaps(self, x: float, y: float, w: int, h: int) -> bool:
        return (
            self.x < x + w
            and x < self.x + self.w
            and self.y < y + h
            and y < self.y + self.h
        )

    def draw(self) -> None:
        pyxel.rect(int(self.x), int(self.y), self.w, self.h, COL_ATTACK)
