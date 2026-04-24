import random

import pyxel

from ..camera import Camera
from ..config import (
    COL_BG,
    COL_HP,
    COL_HP_EMPTY,
    COL_TEXT,
    COL_TEXT_DIM,
    ENEMY_KILL_SHAKE_FRAMES,
    PLAYER_MAX_HP,
    SCREEN_W,
)
from ..enemy import Enemy, Slime
from ..input_handler import InputHandler
from ..particle import Particle, spawn_burst
from ..player import Player
from ..scene import Scene
from ..sfx import SFX_KILL, play_sfx, start_bgm
from ..stage import STAGES
from ..world import World


SCORE_PER_KILL = 100


class PlayScene(Scene):
    def __init__(
        self,
        stage_index: int = 0,
        spawn: tuple[int, int] | None = None,
        hp: int | None = None,
        score: int = 0,
    ) -> None:
        self._stage = STAGES[stage_index]
        self._world = World(self._stage)

        sx, sy = spawn if spawn is not None else self._stage.default_spawn
        self._player = Player(sx, sy)
        if hp is not None:
            self._player.hp = hp

        self._enemies: list[Enemy] = [Slime(x, y) for (x, y) in self._stage.enemy_spawns]
        self._particles: list[Particle] = []
        self._score = score
        self._shake_frames: int = 0
        self._camera = Camera()
        self._update_camera()

    def on_enter(self, manager) -> None:
        super().on_enter(manager)
        start_bgm()

    def update(self, inp: InputHandler) -> None:
        if inp.is_pressed("back"):
            from .pause_scene import PauseScene
            self._manager.push(PauseScene())
            return

        self._player.update(inp, self._world)
        for enemy in self._enemies:
            if enemy.alive:
                enemy.update(self._world, self._player)

        self._resolve_attack_hits()
        self._resolve_enemy_contact()
        self._enemies = [e for e in self._enemies if e.alive]

        for p in self._particles:
            p.update()
        self._particles = [p for p in self._particles if p.alive]

        if self._shake_frames > 0:
            self._shake_frames -= 1

        if not self._player.is_alive:
            from .game_over_scene import GameOverScene
            self._manager.replace(GameOverScene())
            return

        door = self._stage.door_overlapping(
            self._player.x, self._player.y, self._player.w, self._player.h
        )
        if door is not None:
            self._manager.replace(PlayScene(
                stage_index=door.target_stage,
                spawn=door.target_spawn,
                hp=self._player.hp,
                score=self._score,
            ))
            return

        self._update_camera()

    def _update_camera(self) -> None:
        self._camera.follow(
            self._player.x + self._player.w / 2,
            self._player.y + self._player.h / 2,
            self._stage.width,
            self._stage.height,
        )

    def _resolve_attack_hits(self) -> None:
        attack = self._player.attack
        if attack is None:
            return
        for enemy in self._enemies:
            if not enemy.alive:
                continue
            if attack.rect_overlaps(enemy.x, enemy.y, enemy.w, enemy.h):
                enemy.hp -= 1
                if enemy.hp <= 0:
                    enemy.alive = False
                    self._shake_frames = ENEMY_KILL_SHAKE_FRAMES
                    self._score += SCORE_PER_KILL
                    spawn_burst(
                        self._particles,
                        enemy.x + enemy.w / 2,
                        enemy.y + enemy.h / 2,
                        color=14,
                    )
                    play_sfx(SFX_KILL)
                self._player.attack = None
                break

    def _resolve_enemy_contact(self) -> None:
        p = self._player
        for enemy in self._enemies:
            if not enemy.alive:
                continue
            if enemy.rect_overlaps(p.x, p.y, p.w, p.h):
                if p.take_damage(1):
                    break

    def draw(self) -> None:
        pyxel.cls(COL_BG)

        cam_x = int(self._camera.x)
        cam_y = int(self._camera.y)
        if self._shake_frames > 0:
            cam_x += random.randint(-1, 1)
            cam_y += random.randint(-1, 1)
        pyxel.camera(cam_x, cam_y)

        self._world.draw()
        for enemy in self._enemies:
            if enemy.alive:
                enemy.draw()
        self._player.draw()
        for p in self._particles:
            p.draw()

        pyxel.camera()
        self._draw_hud()

    def _draw_hud(self) -> None:
        pyxel.text(2, 2, "ESC: PAUSE", COL_TEXT_DIM)
        pyxel.text(2, 10, f"STAGE {self._stage.index + 1}", COL_TEXT_DIM)
        score_text = f"SCORE {self._score:05d}"
        pyxel.text((SCREEN_W - len(score_text) * 4) // 2, 2, score_text, COL_TEXT)
        for i in range(PLAYER_MAX_HP):
            color = COL_HP if i < self._player.hp else COL_HP_EMPTY
            pyxel.rect(SCREEN_W - 4 - (PLAYER_MAX_HP - i) * 5, 3, 4, 4, color)
