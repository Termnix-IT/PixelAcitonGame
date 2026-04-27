from __future__ import annotations

import os

import pyxel

from .sfx import BGM_BOSS, BGM_ENDING, BGM_PLAY, SFX_ATTACK, SFX_CONFIRM, SFX_HIT, SFX_KILL
from .stage import STAGES

# Sound banks reserved for BGM voices (above the SFX range).
_BGM_MELODY_SND = 8
_BGM_BASS_SND = 9
_BGM_BOSS_LEAD_SND = 10
_BGM_BOSS_BASS_SND = 11
_BGM_ENDING_LEAD_SND = 12

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.normpath(os.path.join(_THIS_DIR, "..", "assets.pyxres"))

# Tileset — (u, v) in tile units on image bank 0.
TILE_FLOOR: tuple[int, int] = (0, 0)
TILE_WALL: tuple[int, int] = (1, 0)
TILE_DOOR: tuple[int, int] = (2, 0)
TILE_SWITCH: tuple[int, int] = (3, 0)
TILE_LOCKED_DOOR: tuple[int, int] = (4, 0)
TILE_KEY: tuple[int, int] = (5, 0)
SOLID_TILES: frozenset[tuple[int, int]] = frozenset({TILE_WALL, TILE_LOCKED_DOOR})

# Sprite atlas — (u, v) in pixels on image bank 0.
SPRITE_W = 8
SPRITE_H = 8
COLKEY = 0

PLAYER_SPRITES: dict[str, list[tuple[int, int]]] = {
    "down":  [(0, 8),  (8, 8)],
    "up":    [(16, 8), (24, 8)],
    "right": [(32, 8), (40, 8)],
}
SLIME_SPRITES: list[tuple[int, int]] = [(0, 16), (8, 16)]
TANK_SPRITES: list[tuple[int, int]] = [(0, 24), (16, 24)]   # 12x12 each
TANK_SPRITE_W = 12
TANK_SPRITE_H = 12
BOSS_SPRITE: tuple[int, int] = (0, 40)                       # 16x16
BOSS_SPRITE_W = 16
BOSS_SPRITE_H = 16


def load_assets() -> None:
    """Populate pyxel image/tilemap banks.

    Loads `assets.pyxres` if present AND current (has stage 2 wired). Otherwise
    paints placeholders from Python and persists a fresh .pyxres so the user
    can refine the art in `pyxel edit assets.pyxres`.
    """
    if os.path.exists(ASSETS_PATH):
        pyxel.load(ASSETS_PATH)
        if _assets_look_current():
            return
        # Stale (Phase 5 or older) — regenerate.
    _build_default_assets()
    try:
        pyxel.save(ASSETS_PATH)
    except Exception:
        pass


def _assets_look_current() -> bool:
    """Heuristic: bumps each time the asset layout changes.

    Verifies stage 4 (boss room) is wired, the new gameplay tiles (switch /
    locked door / key) exist in the image bank, and the boss 16x16 sprite has
    been painted. Also requires SFX to be present.
    """
    tm = pyxel.tilemaps[4]
    has_boss_stage = any(
        tuple(tm.pget(x, y)) != (0, 0)
        for y in range(4)
        for x in range(4)
    )
    img = pyxel.images[0]
    # New gameplay tiles: switch (24,0), locked door (32,0), key (40,0)
    has_new_tiles = (
        img.pget(28, 4) != COLKEY
        and img.pget(36, 4) != COLKEY
        and img.pget(44, 4) != COLKEY
    )
    # Boss sprite center pixel painted
    has_boss = img.pget(8, 48) != COLKEY
    try:
        has_sfx = len(pyxel.sounds[SFX_CONFIRM].notes) > 0
        has_extra_bgm = (
            len(pyxel.sounds[_BGM_BOSS_LEAD_SND].notes) > 0
            and len(pyxel.sounds[_BGM_ENDING_LEAD_SND].notes) > 0
        )
    except Exception:
        has_sfx = False
        has_extra_bgm = False
    return has_boss_stage and has_new_tiles and has_boss and has_sfx and has_extra_bgm


# --- placeholder art ---------------------------------------------------------

_FLOOR = (
    (1, 1, 1, 1, 1, 1, 1, 1),
    (1, 1, 1, 1, 1, 1, 2, 1),
    (1, 1, 1, 1, 1, 1, 1, 1),
    (1, 2, 1, 1, 1, 1, 1, 1),
    (1, 1, 1, 1, 1, 1, 1, 1),
    (1, 1, 1, 1, 1, 2, 1, 1),
    (1, 1, 1, 1, 1, 1, 1, 1),
    (1, 1, 2, 1, 1, 1, 1, 1),
)

_WALL = (
    (6, 6, 6, 6, 6, 6, 6, 6),
    (6, 5, 5, 5, 5, 5, 5, 6),
    (6, 5, 5, 5, 5, 5, 5, 6),
    (6, 5, 5, 5, 5, 5, 5, 6),
    (6, 5, 5, 5, 5, 5, 5, 6),
    (6, 5, 5, 5, 5, 5, 5, 6),
    (6, 5, 5, 5, 5, 5, 5, 6),
    (6, 6, 6, 6, 6, 6, 6, 6),
)

_DOOR = (
    (5, 5, 5, 5, 5, 5, 5, 5),
    (5, 4, 4, 4, 4, 4, 4, 5),
    (5, 4, 4, 4, 4, 4, 4, 5),
    (5, 4, 4, 4, 10, 4, 4, 5),
    (5, 4, 4, 4, 10, 4, 4, 5),
    (5, 4, 4, 4, 4, 4, 4, 5),
    (5, 4, 4, 4, 4, 4, 4, 5),
    (5, 5, 5, 5, 5, 5, 5, 5),
)

_PLAYER_DOWN_0 = (
    (0, 0, 3, 3, 3, 3, 0, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 7, 7, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 0, 3, 3, 3, 3, 0, 0),
    (0, 0, 3, 0, 0, 3, 0, 0),
)
_PLAYER_DOWN_1 = (
    (0, 0, 3, 3, 3, 3, 0, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 7, 7, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 0, 3, 3, 3, 3, 0, 0),
    (0, 3, 0, 0, 0, 0, 3, 0),
)
_PLAYER_UP_0 = (
    (0, 0, 3, 3, 3, 3, 0, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 0, 3, 3, 3, 3, 0, 0),
    (0, 0, 3, 0, 0, 3, 0, 0),
)
_PLAYER_UP_1 = (
    (0, 0, 3, 3, 3, 3, 0, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 0, 3, 3, 3, 3, 0, 0),
    (0, 3, 0, 0, 0, 0, 3, 0),
)
_PLAYER_RIGHT_0 = (
    (0, 0, 3, 3, 3, 3, 0, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 3, 7, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 0, 3, 3, 3, 3, 0, 0),
    (0, 0, 3, 0, 0, 3, 0, 0),
)
_PLAYER_RIGHT_1 = (
    (0, 0, 3, 3, 3, 3, 0, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 3, 7, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 3, 3, 3, 3, 3, 3, 0),
    (0, 0, 3, 3, 3, 3, 0, 0),
    (0, 3, 0, 0, 0, 0, 3, 0),
)

_SLIME_0 = (
    (0,  0,  0, 14, 14,  0,  0,  0),
    (0,  0, 14, 14, 14, 14,  0,  0),
    (0, 14, 14, 14, 14, 14, 14,  0),
    (0, 14, 14,  7, 14,  7, 14,  0),
    (0, 14, 14, 14, 14, 14, 14,  0),
    (14, 14, 14, 14, 14, 14, 14, 14),
    (14, 14, 14, 14, 14, 14, 14, 14),
    (0, 14,  0, 14, 14,  0, 14,  0),
)
_SLIME_1 = (
    (0,  0,  0,  0, 14, 14,  0,  0),
    (0,  0, 14, 14, 14, 14, 14,  0),
    (0, 14, 14, 14, 14, 14, 14, 14),
    (0, 14, 14,  7, 14,  7, 14, 14),
    (0, 14, 14, 14, 14, 14, 14, 14),
    (14, 14, 14, 14, 14, 14, 14, 14),
    (14, 14, 14, 14, 14, 14, 14, 14),
    (0, 14,  0, 14, 14,  0, 14,  0),
)

_SWITCH = (
    (1, 1, 1, 1, 1, 1, 1, 1),
    (1, 1, 1, 1, 1, 1, 1, 1),
    (1, 1, 6, 6, 6, 6, 1, 1),
    (1, 1, 6, 7, 7, 6, 1, 1),
    (1, 1, 6, 7, 7, 6, 1, 1),
    (1, 1, 6, 6, 6, 6, 1, 1),
    (1, 1, 1, 1, 1, 1, 1, 1),
    (1, 1, 1, 1, 1, 1, 1, 1),
)

_LOCKED_DOOR = (
    (5, 5, 5, 5, 5, 5, 5, 5),
    (5, 4, 4, 4, 4, 4, 4, 5),
    (5, 4, 6, 6, 6, 6, 4, 5),
    (5, 4, 6, 0, 0, 6, 4, 5),
    (5, 4, 6, 0, 0, 6, 4, 5),
    (5, 4, 6, 6, 6, 6, 4, 5),
    (5, 4, 4, 4, 4, 4, 4, 5),
    (5, 5, 5, 5, 5, 5, 5, 5),
)

_KEY = (
    (1,  1,  1,  1,  1,  1, 1, 1),
    (1,  1, 10, 10, 10,  1, 1, 1),
    (1,  1, 10,  1,  1,  1, 1, 1),
    (1,  1, 10, 10,  1,  1, 1, 1),
    (1,  1, 10,  1,  1,  1, 1, 1),
    (1,  1, 10,  1,  1,  1, 1, 1),
    (1,  1, 10, 10, 10,  1, 1, 1),
    (1,  1,  1,  1,  1,  1, 1, 1),
)

_TANK_0 = (
    (0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0),
    (0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0),
    (0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0),
    (0, 2, 2, 7, 2, 2, 2, 7, 2, 2, 2, 0),
    (0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0),
    (2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2),
    (2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2),
    (2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2),
    (2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2),
    (0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0),
    (0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0),
    (0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0),
)
_TANK_1 = (
    (0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0),
    (0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0),
    (0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0),
    (0, 2, 2, 2, 7, 2, 2, 2, 7, 2, 2, 0),
    (0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0),
    (2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2),
    (2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2),
    (2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2),
    (2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2),
    (0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0),
    (0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0),
    (0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0),
)

_BOSS = (
    (0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0),
    (0, 0, 0, 1, 1, 5, 5, 5, 5, 5, 5, 1, 1, 0, 0, 0),
    (0, 0, 1, 1, 5, 5, 5, 5, 5, 5, 5, 5, 1, 1, 0, 0),
    (0, 1, 1, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1, 1, 0),
    (0, 1, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1, 0),
    (1, 1, 5, 5, 5, 5,10,10,10,10, 5, 5, 5, 5, 1, 1),
    (1, 5, 5, 5, 5,10, 7, 7, 7, 7,10, 5, 5, 5, 5, 1),
    (1, 5, 5, 5, 5,10, 7,10,10, 7,10, 5, 5, 5, 5, 1),
    (1, 5, 5, 5, 5,10, 7,10,10, 7,10, 5, 5, 5, 5, 1),
    (1, 5, 5, 5, 5,10, 7, 7, 7, 7,10, 5, 5, 5, 5, 1),
    (1, 1, 5, 5, 5, 5,10,10,10,10, 5, 5, 5, 5, 1, 1),
    (0, 1, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1, 0),
    (0, 1, 1, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1, 1, 0),
    (0, 0, 1, 1, 5, 5, 5, 5, 5, 5, 5, 5, 1, 1, 0, 0),
    (0, 0, 0, 1, 1, 5, 5, 5, 5, 5, 5, 1, 1, 0, 0, 0),
    (0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0),
)


def _paint(ox: int, oy: int, pattern: tuple[tuple[int, ...], ...], opaque: bool = False) -> None:
    img = pyxel.images[0]
    for dy, row in enumerate(pattern):
        for dx, c in enumerate(row):
            if not opaque and c == COLKEY:
                continue
            img.pset(ox + dx, oy + dy, c)


def _build_default_assets() -> None:
    _paint(0, 0, _FLOOR, opaque=True)
    _paint(8, 0, _WALL, opaque=True)
    _paint(16, 0, _DOOR, opaque=True)
    _paint(24, 0, _SWITCH, opaque=True)
    _paint(32, 0, _LOCKED_DOOR, opaque=True)
    _paint(40, 0, _KEY, opaque=True)

    _paint(0, 8, _PLAYER_DOWN_0)
    _paint(8, 8, _PLAYER_DOWN_1)
    _paint(16, 8, _PLAYER_UP_0)
    _paint(24, 8, _PLAYER_UP_1)
    _paint(32, 8, _PLAYER_RIGHT_0)
    _paint(40, 8, _PLAYER_RIGHT_1)

    _paint(0, 16, _SLIME_0)
    _paint(8, 16, _SLIME_1)

    _paint(0, 24, _TANK_0)
    _paint(16, 24, _TANK_1)

    _paint(0, 40, _BOSS)

    _build_stage_tilemaps()
    _build_default_sounds()
    _build_default_music()


_TILE_CHAR_MAP: dict[str, tuple[int, int]] = {
    "1": TILE_WALL,
    "D": TILE_DOOR,
    "S": TILE_SWITCH,
    "L": TILE_LOCKED_DOOR,
    "K": TILE_KEY,
}


def _build_stage_tilemaps() -> None:
    for stage in STAGES:
        tm = pyxel.tilemaps[stage.index]
        for ty in range(stage.height):
            row = stage.raw_map[ty]
            for tx in range(stage.width):
                c = row[tx]
                tm.pset(tx, ty, _TILE_CHAR_MAP.get(c, TILE_FLOOR))


def _build_default_sounds() -> None:
    # Attack: quick high chirp (square wave, fade out).
    pyxel.sounds[SFX_ATTACK].set(
        notes="f4a4", tones="p", volumes="6", effects="f", speed=6,
    )
    # Hit: low noise thud.
    pyxel.sounds[SFX_HIT].set(
        notes="c1", tones="n", volumes="7", effects="f", speed=16,
    )
    # Kill: descending triangle arpeggio with a fade.
    pyxel.sounds[SFX_KILL].set(
        notes="g4e4c4", tones="t", volumes="7", effects="f", speed=7,
    )
    # Confirm: short ascending pulse.
    pyxel.sounds[SFX_CONFIRM].set(
        notes="c3g3", tones="p", volumes="5", effects="n", speed=10,
    )


def _build_default_music() -> None:
    # 16-note melody on channel 0 (triangle): simple i–V arpeggio loop.
    pyxel.sounds[_BGM_MELODY_SND].set(
        notes="c3e3g3c4c4g3e3c3f3a3c4f4f4c4a3f3",
        tones="t",
        volumes="4",
        effects="n",
        speed=18,
    )
    # Sustained bass on channel 1 (pulse): root-fifth pedal.
    pyxel.sounds[_BGM_BASS_SND].set(
        notes="c2rrg2rrc2rrg2rrf2rrc2rrf2rrc2rr",
        tones="p",
        volumes="3",
        effects="n",
        speed=18,
    )
    pyxel.musics[BGM_PLAY].set(
        [_BGM_MELODY_SND], [_BGM_BASS_SND], [], [],
    )

    # Boss BGM: pulsing minor riff with a relentless low pedal.
    pyxel.sounds[_BGM_BOSS_LEAD_SND].set(
        notes="c2d2e-2d2c2d2e-2d2f2g2a-2g2f2g2a-2g2",
        tones="s",
        volumes="5",
        effects="n",
        speed=14,
    )
    pyxel.sounds[_BGM_BOSS_BASS_SND].set(
        notes="c1c1c1c1c1c1c1c1f1f1f1f1f1f1f1f1",
        tones="p",
        volumes="4",
        effects="n",
        speed=14,
    )
    pyxel.musics[BGM_BOSS].set(
        [_BGM_BOSS_LEAD_SND], [_BGM_BOSS_BASS_SND], [], [],
    )

    # Ending BGM: slow ascending triangle, single voice for stillness.
    pyxel.sounds[_BGM_ENDING_LEAD_SND].set(
        notes="c4rg4re4rc4rg3rc4re4rg4r",
        tones="t",
        volumes="3",
        effects="n",
        speed=30,
    )
    pyxel.musics[BGM_ENDING].set(
        [_BGM_ENDING_LEAD_SND], [], [], [],
    )
