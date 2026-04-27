from __future__ import annotations

import math
import random

import pyxel

from ..assets import COLKEY, PLAYER_SPRITES, SPRITE_H, SPRITE_W
from ..config import COL_BG, COL_TEXT, COL_TEXT_DIM, SCREEN_H, SCREEN_W
from ..input_handler import InputHandler
from ..particle import Particle
from ..scene import Scene
from ..sfx import BGM_ENDING, SFX_CONFIRM, play_sfx, start_bgm, stop_bgm


# Timing breakpoints in frames. Phase markers stack in order.
_T_DROP_END = 30        # golden drop has reached the surface
_T_WATER_END = 90       # water surface line has finished spreading
_T_TEXT_FADE = 150      # the closing line fades in
_T_INPUT_OPEN = 180     # PRESS SPACE prompt and confirm input become live


class EndingScene(Scene):
    """Four-stage closing cinematic.

    1. drop:       a golden drop falls from the top of the screen
    2. impact:     burst on landing, water surface line begins spreading
    3. surface:    the surface line stretches outward to the screen edges
    4. silhouette: the shrine keeper's outline appears with rising sparkles,
                   then the closing line fades in and the prompt opens up
    """

    _LINE_1 = "THE SHRINE SLEEPS AGAIN."

    def on_enter(self, manager) -> None:
        super().on_enter(manager)
        stop_bgm()
        start_bgm(BGM_ENDING)
        self._timer = 0
        self._burst_particles: list[Particle] = []
        self._ambient_particles: list[Particle] = []
        self._impacted = False

    def update(self, inp: InputHandler) -> None:
        self._timer += 1

        if not self._impacted and self._timer >= _T_DROP_END:
            self._impacted = True
            self._spawn_impact_burst()
            play_sfx(SFX_CONFIRM)

        if self._timer >= _T_WATER_END and self._timer % 6 == 0:
            self._spawn_ambient()

        for p in self._burst_particles:
            p.update()
        self._burst_particles = [p for p in self._burst_particles if p.alive]

        for p in self._ambient_particles:
            p.update()
        self._ambient_particles = [
            p for p in self._ambient_particles if p.alive and p.y > -2
        ]

        if self._timer > _T_INPUT_OPEN and inp.is_pressed("confirm"):
            play_sfx(SFX_CONFIRM)
            from .title_scene import TitleScene
            self._manager.replace(TitleScene())

    def _spawn_impact_burst(self) -> None:
        cx = SCREEN_W / 2
        cy = SCREEN_H / 2
        for _ in range(20):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(0.5, 2.0)
            self._burst_particles.append(
                Particle(
                    cx, cy,
                    math.cos(ang) * spd,
                    math.sin(ang) * spd,
                    10,
                    random.randint(20, 40),
                )
            )

    def _spawn_ambient(self) -> None:
        self._ambient_particles.append(
            Particle(
                x=random.uniform(0, SCREEN_W),
                y=SCREEN_H + 2,
                vx=random.uniform(-0.05, 0.05),
                vy=-random.uniform(0.15, 0.35),
                color=random.choice((6, 12, 13)),
                life=random.randint(120, 200),
                gravity=0.0,
                drag=1.0,
            )
        )

    def draw(self) -> None:
        pyxel.camera()
        pyxel.cls(COL_BG)

        cx = SCREEN_W // 2
        cy = SCREEN_H // 2

        # Stage 1: golden drop, accelerating downward (ease-in via t²).
        if self._timer < _T_DROP_END:
            t = self._timer / _T_DROP_END
            drop_y = int(t * t * cy)
            pyxel.rect(cx - 2, drop_y - 2, 4, 4, 10)

        # Stage 2/3: water surface spreading from the impact point.
        if self._timer >= _T_DROP_END:
            spread_t = min(
                1.0, (self._timer - _T_DROP_END) / (_T_WATER_END - _T_DROP_END)
            )
            half = int(spread_t * (SCREEN_W / 2))
            pyxel.line(cx - half, cy, cx + half, cy, 12)
            if spread_t > 0.3:
                pyxel.line(cx - half, cy + 1, cx + half, cy + 1, 1)

        # Stage 4: silhouette + rising sparkles, drawn before the burst.
        if self._timer >= _T_WATER_END:
            for p in self._ambient_particles:
                p.draw()
            u, v = PLAYER_SPRITES["down"][0]
            sx = cx - SPRITE_W // 2
            sy = cy - SPRITE_H - 2
            # Recolor the keeper to a shadow tone — the body (3) and accent (7)
            # both collapse to the darkest navy (1).
            pyxel.pal(3, 1)
            pyxel.pal(7, 1)
            pyxel.blt(sx, sy, 0, u, v, SPRITE_W, SPRITE_H, COLKEY)
            pyxel.pal()

        # Impact burst draws over the surface line briefly.
        for p in self._burst_particles:
            p.draw()

        # Stage 5: closing line fades in.
        if self._timer >= _T_TEXT_FADE:
            tx = (SCREEN_W - len(self._LINE_1) * 4) // 2
            pyxel.text(tx, SCREEN_H - 24, self._LINE_1, COL_TEXT)

        if self._timer > _T_INPUT_OPEN and (pyxel.frame_count // 20) % 2 == 0:
            tip = "PRESS SPACE"
            pyxel.text(
                (SCREEN_W - len(tip) * 4) // 2, SCREEN_H - 12, tip, COL_TEXT_DIM
            )
