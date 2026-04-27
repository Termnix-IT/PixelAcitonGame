from __future__ import annotations

from typing import Callable

import pyxel

from ..config import COL_BG, COL_TEXT, COL_TEXT_DIM, SCREEN_H, SCREEN_W
from ..input_handler import InputHandler
from ..scene import Scene
from ..sfx import SFX_CONFIRM, play_sfx, stop_bgm


class StoryScene(Scene):
    """Inter-stage chapter card. Confirm to continue to the next factory-built scene."""

    def __init__(self, chapter_title: str, next_factory: Callable[[], Scene]) -> None:
        self._title = chapter_title
        self._next_factory = next_factory

    def on_enter(self, manager) -> None:
        super().on_enter(manager)
        stop_bgm()

    def update(self, inp: InputHandler) -> None:
        if inp.is_pressed("confirm"):
            play_sfx(SFX_CONFIRM)
            self._manager.replace(self._next_factory())

    def draw(self) -> None:
        pyxel.camera()
        pyxel.cls(COL_BG)

        tx = (SCREEN_W - len(self._title) * 4) // 2
        pyxel.text(tx, SCREEN_H // 2 - 8, self._title, COL_TEXT)

        if (pyxel.frame_count // 20) % 2 == 0:
            tip = "PRESS SPACE"
            pyxel.text((SCREEN_W - len(tip) * 4) // 2, SCREEN_H // 2 + 12, tip, COL_TEXT_DIM)
