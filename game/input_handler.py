import math

import pyxel


class InputHandler:
    def __init__(self, keybinds: dict[str, list[int]]):
        self._binds = keybinds

    def is_down(self, action: str) -> bool:
        return any(pyxel.btn(k) for k in self._binds.get(action, ()))

    def is_pressed(self, action: str) -> bool:
        return any(pyxel.btnp(k) for k in self._binds.get(action, ()))

    def is_released(self, action: str) -> bool:
        return any(pyxel.btnr(k) for k in self._binds.get(action, ()))

    def axis(self, neg_action: str, pos_action: str) -> int:
        neg = self.is_down(neg_action)
        pos = self.is_down(pos_action)
        return (1 if pos else 0) - (1 if neg else 0)

    def move_vector(self) -> tuple[float, float]:
        dx = self.axis("move_left", "move_right")
        dy = self.axis("move_up", "move_down")
        if dx != 0 and dy != 0:
            inv = 1.0 / math.sqrt(2)
            return dx * inv, dy * inv
        return float(dx), float(dy)
