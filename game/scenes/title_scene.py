import math
import random

import pyxel

from ..config import COL_BG, COL_TEXT, COL_TEXT_DIM, SCREEN_H, SCREEN_W
from ..input_handler import InputHandler
from ..particle import Particle
from ..scene import Scene
from ..sfx import SFX_CONFIRM, play_sfx, stop_bgm
from ..stage import STAGES


class TitleScene(Scene):
    def __init__(self) -> None:
        self._bg_particles: list[Particle] = []

    def on_enter(self, manager) -> None:
        super().on_enter(manager)
        stop_bgm()

    def update(self, inp: InputHandler) -> None:
        if random.random() < 0.2:
            self._bg_particles.append(
                Particle(
                    x=random.uniform(0, SCREEN_W),
                    y=SCREEN_H + 2,
                    vx=random.uniform(-0.1, 0.1),
                    vy=-random.uniform(0.2, 0.6),
                    color=random.choice((5, 6, 13)),
                    life=random.randint(120, 200),
                    gravity=0.0,
                    drag=1.0,
                )
            )
        for p in self._bg_particles:
            p.update()
        self._bg_particles = [p for p in self._bg_particles if p.alive and p.y > -2]

        if inp.is_pressed("confirm"):
            play_sfx(SFX_CONFIRM)
            from .play_scene import PlayScene
            from .story_scene import StoryScene
            self._manager.replace(
                StoryScene(STAGES[0].chapter_title, lambda: PlayScene())
            )

    def draw(self) -> None:
        pyxel.camera()
        pyxel.cls(COL_BG)

        for p in self._bg_particles:
            p.draw()

        wave = int(math.sin(pyxel.frame_count * 0.08) * 2)
        title = "PIXEL ACTION"
        pyxel.text((SCREEN_W - len(title) * 4) // 2, SCREEN_H // 2 - 16 + wave, title, COL_TEXT)

        subtitle = "THE SUNKEN SHRINE"
        pyxel.text((SCREEN_W - len(subtitle) * 4) // 2, SCREEN_H // 2 - 4, subtitle, COL_TEXT_DIM)

        tip = "PRESS SPACE"
        if (pyxel.frame_count // 20) % 2 == 0:
            pyxel.text((SCREEN_W - len(tip) * 4) // 2, SCREEN_H // 2 + 14, tip, COL_TEXT_DIM)
