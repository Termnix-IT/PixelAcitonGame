import random

import pyxel

from ..assets import (
    COLKEY,
    TILE_FLOOR,
    TILE_KEY,
    TILE_LOCKED_DOOR,
)
from ..boss import Boss
from ..camera import Camera
from ..config import (
    BOSS_HP,
    BOSS_KILL_BURST_COUNT,
    BOSS_KILL_SHAKE_FRAMES,
    BOSS_PHASE_A_MIN_HP,
    BOSS_PHASE_B_MIN_HP,
    COL_BG,
    COL_HP,
    COL_HP_EMPTY,
    COL_TEXT,
    COL_TEXT_DIM,
    ENEMY_KILL_SHAKE_FRAMES,
    LEVEL_COOLDOWNS,
    LEVEL_DAMAGES,
    LEVEL_THRESHOLDS,
    LEVEL_UP_DISPLAY_FRAMES,
    PLAYER_MAX_HP,
    SCREEN_H,
    SCREEN_W,
    TILE_SIZE,
)
from ..enemy import DashSlime, Enemy, RangedSlime, Slime, TankSlime
from ..input_handler import InputHandler
from ..particle import Particle, spawn_burst
from ..player import Player
from ..projectile import Projectile
from ..scene import Scene
from ..sfx import BGM_BOSS, BGM_PLAY, SFX_CONFIRM, SFX_KILL, play_sfx, start_bgm
from ..stage import STAGES
from ..world import World


SCORE_PER_KILL = 100
SCORE_PER_BOSS = 1000
KEY_HUD_U = 40   # locked-key tile at (5, 0) in tile coords → (40, 0) px


def _level_for_score(score: int) -> int:
    """Highest level whose threshold has been reached. Levels are 1-indexed."""
    level = 1
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if score >= threshold:
            level = i + 1
    return max(1, level)


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

        # Reset stage-local gimmick tiles so re-entering a stage starts fresh.
        self._reset_gimmick_tiles()

        self._enemies: list[Enemy] = []
        for x, y in self._stage.enemy_spawns:
            self._enemies.append(Slime(x, y))
        for x, y in self._stage.dash_spawns:
            self._enemies.append(DashSlime(x, y))
        for x, y in self._stage.tank_spawns:
            self._enemies.append(TankSlime(x, y))
        self._ranged_slimes: list[RangedSlime] = []
        for x, y in self._stage.ranged_spawns:
            r = RangedSlime(x, y)
            self._ranged_slimes.append(r)
            self._enemies.append(r)

        self._boss: Boss | None = None
        if self._stage.boss_spawn is not None:
            bx, by = self._stage.boss_spawn
            self._boss = Boss(bx, by)
            self._enemies.append(self._boss)

        self._enemy_projectiles: list[Projectile] = []
        self._has_key = False
        self._particles: list[Particle] = []
        self._score = score
        self._level = _level_for_score(score)
        self._player.shoot_cooldown_max = LEVEL_COOLDOWNS[self._level - 1]
        self._level_up_timer = 0
        self._shake_frames: int = 0
        self._camera = Camera()
        self._update_camera()

    def on_enter(self, manager) -> None:
        super().on_enter(manager)
        start_bgm(BGM_BOSS if self._stage.boss_spawn is not None else BGM_PLAY)

    def _reset_gimmick_tiles(self) -> None:
        tm = pyxel.tilemaps[self._stage.index]
        for sg in self._stage.switch_gates:
            tm.pset(sg.door[0], sg.door[1], TILE_LOCKED_DOOR)
        for kg in self._stage.key_gates:
            tm.pset(kg.door[0], kg.door[1], TILE_LOCKED_DOOR)
            tm.pset(kg.key[0], kg.key[1], TILE_KEY)

    def update(self, inp: InputHandler) -> None:
        if inp.is_pressed("back"):
            from .pause_scene import PauseScene
            self._manager.push(PauseScene())
            return

        self._player.update(inp, self._world)
        for enemy in self._enemies:
            if enemy.alive:
                enemy.update(self._world, self._player)

        if self._boss is not None and self._boss.alive:
            self._enemy_projectiles.extend(self._boss.take_pending_projectiles())
        for r in self._ranged_slimes:
            if r.alive:
                self._enemy_projectiles.extend(r.take_pending_projectiles())

        for p in self._enemy_projectiles:
            p.update(self._world)
        self._resolve_enemy_projectile_hits()
        self._enemy_projectiles = [p for p in self._enemy_projectiles if not p.is_expired()]

        self._resolve_projectile_hits()
        self._resolve_enemy_contact()
        self._resolve_gimmicks()
        self._enemies = [e for e in self._enemies if e.alive]

        # Boss kill → ending. Boss is removed from _enemies above; check the cached ref.
        if self._boss is not None and not self._boss.alive:
            from .ending_scene import EndingScene
            self._manager.replace(EndingScene())
            return

        for p in self._particles:
            p.update()
        self._particles = [p for p in self._particles if p.alive]

        if self._shake_frames > 0:
            self._shake_frames -= 1
        if self._level_up_timer > 0:
            self._level_up_timer -= 1

        if not self._player.is_alive:
            from .game_over_scene import GameOverScene
            self._manager.replace(GameOverScene())
            return

        door = self._stage.door_overlapping(
            self._player.x, self._player.y, self._player.w, self._player.h
        )
        if door is not None:
            self._handle_door(door)
            return

        self._update_camera()

    def _handle_door(self, door) -> None:
        next_factory = lambda: PlayScene(
            stage_index=door.target_stage,
            spawn=door.target_spawn,
            hp=self._player.hp,
            score=self._score,
        )
        if door.target_stage > self._stage.index:
            from .story_scene import StoryScene
            target_stage = STAGES[door.target_stage]
            self._manager.replace(StoryScene(target_stage.chapter_title, next_factory))
        else:
            self._manager.replace(next_factory())

    def _update_camera(self) -> None:
        self._camera.follow(
            self._player.x + self._player.w / 2,
            self._player.y + self._player.h / 2,
            self._stage.width,
            self._stage.height,
        )

    def _resolve_projectile_hits(self) -> None:
        if not self._player.projectiles:
            return
        damage = LEVEL_DAMAGES[self._level - 1]
        for proj in self._player.projectiles:
            if proj.is_expired():
                continue
            for enemy in self._enemies:
                if not enemy.alive:
                    continue
                if proj.rect_overlaps(enemy.x, enemy.y, enemy.w, enemy.h):
                    self._apply_hit(enemy, damage=damage)
                    proj.expire()
                    break

    def _resolve_enemy_projectile_hits(self) -> None:
        p = self._player
        for proj in self._enemy_projectiles:
            if proj.is_expired():
                continue
            if proj.rect_overlaps(p.x, p.y, p.w, p.h):
                if p.take_damage(1):
                    proj.expire()

    def _apply_hit(self, enemy: Enemy, damage: int = 1) -> None:
        enemy.hp -= damage
        if enemy.hp <= 0:
            enemy.alive = False
            if isinstance(enemy, Boss):
                self._shake_frames = BOSS_KILL_SHAKE_FRAMES
                self._score += SCORE_PER_BOSS
                spawn_burst(
                    self._particles,
                    enemy.x + enemy.w / 2,
                    enemy.y + enemy.h / 2,
                    color=10,
                    count=BOSS_KILL_BURST_COUNT,
                )
                play_sfx(SFX_KILL)
            else:
                self._shake_frames = ENEMY_KILL_SHAKE_FRAMES
                self._score += SCORE_PER_KILL
                spawn_burst(
                    self._particles,
                    enemy.x + enemy.w / 2,
                    enemy.y + enemy.h / 2,
                    color=14,
                )
                play_sfx(SFX_KILL)
                if isinstance(enemy, TankSlime):
                    self._spawn_split(enemy)
            self._check_level_up()

    def _check_level_up(self) -> None:
        new_level = _level_for_score(self._score)
        if new_level > self._level:
            self._level = new_level
            self._player.shoot_cooldown_max = LEVEL_COOLDOWNS[self._level - 1]
            self._level_up_timer = LEVEL_UP_DISPLAY_FRAMES
            play_sfx(SFX_CONFIRM)

    def _spawn_split(self, tank: TankSlime) -> None:
        cx = tank.x + tank.w / 2
        cy = tank.y + tank.h / 2
        for ox, oy in ((-4.0, -2.0), (4.0, 2.0)):
            self._enemies.append(Slime(cx + ox - 3, cy + oy - 3))

    def _resolve_enemy_contact(self) -> None:
        p = self._player
        for enemy in self._enemies:
            if not enemy.alive:
                continue
            if enemy.rect_overlaps(p.x, p.y, p.w, p.h):
                if p.take_damage(enemy.contact_damage):
                    break

    def _resolve_gimmicks(self) -> None:
        tm = pyxel.tilemaps[self._stage.index]
        for sg in self._stage.switch_gates:
            if self._tile_overlaps_player(*sg.switch):
                if tuple(tm.pget(sg.door[0], sg.door[1])) == TILE_LOCKED_DOOR:
                    tm.pset(sg.door[0], sg.door[1], TILE_FLOOR)
                    play_sfx(SFX_CONFIRM)
        for kg in self._stage.key_gates:
            if not self._has_key and tuple(tm.pget(kg.key[0], kg.key[1])) == TILE_KEY:
                if self._tile_overlaps_player(*kg.key):
                    self._has_key = True
                    tm.pset(kg.key[0], kg.key[1], TILE_FLOOR)
                    play_sfx(SFX_CONFIRM)
            if self._has_key and tuple(tm.pget(kg.door[0], kg.door[1])) == TILE_LOCKED_DOOR:
                if self._tile_overlaps_player(*kg.door):
                    tm.pset(kg.door[0], kg.door[1], TILE_FLOOR)
                    play_sfx(SFX_CONFIRM)

    def _tile_overlaps_player(self, tx: int, ty: int) -> bool:
        p = self._player
        x0 = tx * TILE_SIZE
        y0 = ty * TILE_SIZE
        return (
            p.x < x0 + TILE_SIZE
            and x0 < p.x + p.w
            and p.y < y0 + TILE_SIZE
            and y0 < p.y + p.h
        )

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
        for p in self._enemy_projectiles:
            p.draw()
        self._player.draw()
        for p in self._particles:
            p.draw()

        pyxel.camera()
        self._draw_hud()

    def _draw_hud(self) -> None:
        pyxel.text(2, 2, "ESC: PAUSE", COL_TEXT_DIM)
        pyxel.text(2, 10, f"STAGE {self._stage.index + 1}", COL_TEXT_DIM)
        pyxel.text(2, 18, f"LV {self._level}", COL_TEXT)
        score_text = f"SCORE {self._score:05d}"
        pyxel.text((SCREEN_W - len(score_text) * 4) // 2, 2, score_text, COL_TEXT)
        for i in range(PLAYER_MAX_HP):
            color = COL_HP if i < self._player.hp else COL_HP_EMPTY
            pyxel.rect(SCREEN_W - 4 - (PLAYER_MAX_HP - i) * 5, 3, 4, 4, color)
        if self._has_key:
            # Lit key icon to the left of the HP row.
            pyxel.blt(SCREEN_W - 4 - PLAYER_MAX_HP * 5 - 10, 1, 0, KEY_HUD_U, 0, 8, 8, COLKEY)
        self._draw_boss_hp_bar()
        if self._level_up_timer > 0 and (self._level_up_timer // 4) % 2 == 0:
            banner = "LEVEL UP!"
            pyxel.text((SCREEN_W - len(banner) * 4) // 2, SCREEN_H // 2 - 4, banner, COL_TEXT)

    def _draw_boss_hp_bar(self) -> None:
        if self._boss is None or not self._boss.alive:
            return

        bar_w = 120
        bar_h = 6
        bar_x = (SCREEN_W - bar_w) // 2
        bar_y = 22
        label = "THE CORE"
        pyxel.text((SCREEN_W - len(label) * 4) // 2, bar_y - 8, label, COL_TEXT)

        # Outer frame in dim gray, inner background in deep navy.
        pyxel.rectb(bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2, 5)
        pyxel.rect(bar_x, bar_y, bar_w, bar_h, 1)

        if self._boss.hp >= BOSS_PHASE_A_MIN_HP:
            fill_color = 10   # gold — Phase A
        elif self._boss.hp >= BOSS_PHASE_B_MIN_HP:
            fill_color = 9    # orange — Phase B
        else:
            fill_color = 8    # red — Phase C

        fill_w = int(bar_w * self._boss.hp / BOSS_HP)
        if fill_w > 0:
            pyxel.rect(bar_x, bar_y, fill_w, bar_h, fill_color)
