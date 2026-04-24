from __future__ import annotations

import os

import pyxel

from .sfx import BGM_PLAY, SFX_ATTACK, SFX_CONFIRM, SFX_HIT, SFX_KILL
from .stage import STAGES

# Sound banks reserved for BGM voices (above the SFX range).
_BGM_MELODY_SND = 8
_BGM_BASS_SND = 9

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.normpath(os.path.join(_THIS_DIR, "..", "assets.pyxres"))

# Tileset — (u, v) in tile units on image bank 0.
TILE_FLOOR: tuple[int, int] = (0, 0)
TILE_WALL: tuple[int, int] = (1, 0)
TILE_DOOR: tuple[int, int] = (2, 0)
SOLID_TILES: frozenset[tuple[int, int]] = frozenset({TILE_WALL})

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
    """Heuristic: Phase 6 added stage 2, Phase 7 added SFX."""
    tm = pyxel.tilemaps[1]
    has_stage_2 = any(
        tuple(tm.pget(x, y)) != (0, 0)
        for y in range(4)
        for x in range(4)
    )
    try:
        has_sfx = len(pyxel.sounds[SFX_CONFIRM].notes) > 0
    except Exception:
        has_sfx = False
    return has_stage_2 and has_sfx


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

    _paint(0, 8, _PLAYER_DOWN_0)
    _paint(8, 8, _PLAYER_DOWN_1)
    _paint(16, 8, _PLAYER_UP_0)
    _paint(24, 8, _PLAYER_UP_1)
    _paint(32, 8, _PLAYER_RIGHT_0)
    _paint(40, 8, _PLAYER_RIGHT_1)

    _paint(0, 16, _SLIME_0)
    _paint(8, 16, _SLIME_1)

    _build_stage_tilemaps()
    _build_default_sounds()
    _build_default_music()


def _build_stage_tilemaps() -> None:
    for stage in STAGES:
        tm = pyxel.tilemaps[stage.index]
        for ty in range(stage.height):
            row = stage.raw_map[ty]
            for tx in range(stage.width):
                c = row[tx]
                if c == "1":
                    tm.pset(tx, ty, TILE_WALL)
                elif c == "D":
                    tm.pset(tx, ty, TILE_DOOR)
                else:
                    tm.pset(tx, ty, TILE_FLOOR)


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
