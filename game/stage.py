from __future__ import annotations

import random
from dataclasses import dataclass

from .config import STAGE_H, STAGE_W, TILE_SIZE


@dataclass(frozen=True)
class Door:
    tx: int
    ty: int
    target_stage: int
    target_spawn: tuple[int, int]  # pixel coordinates

    @property
    def pixel_rect(self) -> tuple[int, int, int, int]:
        return (self.tx * TILE_SIZE, self.ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)


@dataclass(frozen=True)
class SwitchGate:
    switch: tuple[int, int]   # tile coords of the floor switch
    door: tuple[int, int]     # tile coords of the locked door it opens


@dataclass(frozen=True)
class KeyGate:
    key: tuple[int, int]      # tile coords of the key pickup
    door: tuple[int, int]     # tile coords of the locked door it opens


@dataclass(frozen=True)
class Stage:
    index: int
    width: int
    height: int
    raw_map: tuple[str, ...]
    default_spawn: tuple[int, int]
    enemy_spawns: tuple[tuple[int, int], ...]
    doors: tuple[Door, ...]
    dash_spawns: tuple[tuple[int, int], ...] = ()
    tank_spawns: tuple[tuple[int, int], ...] = ()
    ranged_spawns: tuple[tuple[int, int], ...] = ()
    boss_spawn: tuple[int, int] | None = None
    switch_gates: tuple[SwitchGate, ...] = ()
    key_gates: tuple[KeyGate, ...] = ()
    chapter_title: str = ""

    def door_overlapping(self, x: float, y: float, w: int, h: int) -> Door | None:
        for door in self.doors:
            dx, dy, dw, dh = door.pixel_rect
            if x < dx + dw and dx < x + w and y < dy + dh and dy < y + h:
                return door
        return None


def _generate(
    seed: int,
    doors: tuple[tuple[int, int], ...],
    safe_tiles: tuple[tuple[int, int], ...],
) -> tuple[tuple[str, ...], tuple[tuple[int, int], ...]]:
    """Build a reproducible raw map and pick enemy spawn tiles."""
    rng = random.Random(seed)
    m: list[list[str]] = [["0"] * STAGE_W for _ in range(STAGE_H)]

    for x in range(STAGE_W):
        m[0][x] = "1"
        m[STAGE_H - 1][x] = "1"
    for y in range(STAGE_H):
        m[y][0] = "1"
        m[y][STAGE_W - 1] = "1"

    for _ in range(22):
        cx = rng.randint(3, STAGE_W - 5)
        cy = rng.randint(3, STAGE_H - 5)
        cw = rng.randint(2, 4)
        ch = rng.randint(1, 3)
        for yy in range(cy, min(cy + ch, STAGE_H - 1)):
            for xx in range(cx, min(cx + cw, STAGE_W - 1)):
                m[yy][xx] = "1"

    for sx, sy in safe_tiles:
        m[sy][sx] = "0"

    for dx, dy in doors:
        m[dy][dx] = "D"

    spawns: list[tuple[int, int]] = []
    for _ in range(400):
        x = rng.randint(2, STAGE_W - 3)
        y = rng.randint(2, STAGE_H - 3)
        if m[y][x] == "0":
            spawns.append((x * TILE_SIZE, y * TILE_SIZE))
            if len(spawns) >= 6:
                break

    raw = tuple("".join(row) for row in m)
    return raw, tuple(spawns)


def _patch(raw: tuple[str, ...], patches: tuple[tuple[int, int, str], ...]) -> tuple[str, ...]:
    """Overlay individual tile characters onto a raw map."""
    rows = [list(r) for r in raw]
    for x, y, c in patches:
        rows[y][x] = c
    return tuple("".join(r) for r in rows)


def _boss_room() -> tuple[tuple[str, ...], tuple[int, int], tuple[int, int]]:
    """Hand-built closed square room for the final boss.

    Returns (raw_map, entrance_door_tile, boss_center_tile).
    """
    rows = [["1"] * STAGE_W for _ in range(STAGE_H)]
    room_w, room_h = 16, 12
    rx0 = (STAGE_W - room_w) // 2
    rx1 = rx0 + room_w
    ry0 = (STAGE_H - room_h) // 2
    ry1 = ry0 + room_h
    for y in range(ry0, ry1):
        for x in range(rx0, rx1):
            rows[y][x] = "0"
    # West entrance corridor: 2 floor tiles + 1 door
    door_y = (ry0 + ry1) // 2
    rows[door_y][rx0 - 1] = "0"
    rows[door_y][rx0 - 2] = "D"
    boss_center = (rx0 + room_w // 2, ry0 + room_h // 2)
    raw = tuple("".join(r) for r in rows)
    return raw, (rx0 - 2, door_y), boss_center


_MID_Y = STAGE_H // 2

# --- Stage 0: THE ENTRANCE ---------------------------------------------------
_S0_DOORS = ((STAGE_W - 1, _MID_Y),)
_S0_SAFE = ((2, 2), (STAGE_W - 2, _MID_Y), (STAGE_W - 3, _MID_Y))
_S0_MAP, _S0_ENEMIES = _generate(seed=1, doors=_S0_DOORS, safe_tiles=_S0_SAFE)

# --- Stage 1: THE MOSS HALL (switch gate + dash slimes) ----------------------
# Switch in the open mid-area, locked door blocks the run-up to the east exit.
_S1_SWITCH = (STAGE_W // 2, _MID_Y - 3)
_S1_LOCKED = (STAGE_W - 3, _MID_Y)
_S1_DOORS_TILES = ((STAGE_W - 1, _MID_Y),)
_S1_SAFE = (
    (1, _MID_Y), (2, _MID_Y),
    _S1_SWITCH,
    _S1_LOCKED, (STAGE_W - 4, _MID_Y), (STAGE_W - 2, _MID_Y),
)
_S1_MAP_RAW, _S1_ENEMIES_ALL = _generate(seed=2, doors=_S1_DOORS_TILES, safe_tiles=_S1_SAFE)
_S1_MAP = _patch(
    _S1_MAP_RAW,
    (
        (_S1_SWITCH[0], _S1_SWITCH[1], "S"),
        (_S1_LOCKED[0], _S1_LOCKED[1], "L"),
    ),
)
# Half normal slimes, half dash slimes for early variety.
_S1_NORMAL = _S1_ENEMIES_ALL[: len(_S1_ENEMIES_ALL) // 2]
_S1_DASH = _S1_ENEMIES_ALL[len(_S1_ENEMIES_ALL) // 2 :]

# --- Stage 2: THE DRIPPING CORRIDOR (all dash slimes) ------------------------
_S2_DOORS_TILES = ((STAGE_W - 1, _MID_Y),)
_S2_SAFE = ((1, _MID_Y), (2, _MID_Y), (STAGE_W - 2, _MID_Y), (STAGE_W - 3, _MID_Y))
_S2_MAP, _S2_ENEMIES_ALL = _generate(seed=3, doors=_S2_DOORS_TILES, safe_tiles=_S2_SAFE)
# Mid-stage shake-up: keep most as dash, convert two to ranged shooters.
_S2_DASH = _S2_ENEMIES_ALL[:4]
_S2_RANGED = _S2_ENEMIES_ALL[4:]

# --- Stage 3: THE SPRING GATE (tank + key gate) ------------------------------
# Key sits exposed near west, locked door blocks east stage exit.
_S3_KEY = (STAGE_W // 3, _MID_Y)
_S3_LOCKED = (STAGE_W - 3, _MID_Y)
_S3_TANK_TILE = (STAGE_W * 2 // 3, _MID_Y)
_S3_DOORS_TILES = ((STAGE_W - 1, _MID_Y),)
_S3_SAFE = (
    (1, _MID_Y), (2, _MID_Y),
    _S3_KEY,
    _S3_TANK_TILE,
    _S3_LOCKED, (STAGE_W - 4, _MID_Y), (STAGE_W - 2, _MID_Y),
)
_S3_MAP_RAW, _S3_ENEMIES_ALL = _generate(seed=4, doors=_S3_DOORS_TILES, safe_tiles=_S3_SAFE)
_S3_MAP = _patch(
    _S3_MAP_RAW,
    (
        (_S3_KEY[0], _S3_KEY[1], "K"),
        (_S3_LOCKED[0], _S3_LOCKED[1], "L"),
    ),
)
# Keep 4 plain slimes; pin the tank at the chosen tile.
_S3_NORMAL = _S3_ENEMIES_ALL[:4]
_S3_TANK = ((_S3_TANK_TILE[0] * TILE_SIZE, _S3_TANK_TILE[1] * TILE_SIZE),)

# --- Stage 4: THE CORE (boss room) -------------------------------------------
_S4_MAP, _S4_ENTRANCE, _S4_BOSS_TILE = _boss_room()


STAGES: tuple[Stage, ...] = (
    Stage(
        index=0,
        width=STAGE_W,
        height=STAGE_H,
        raw_map=_S0_MAP,
        default_spawn=(2 * TILE_SIZE, 2 * TILE_SIZE),
        enemy_spawns=_S0_ENEMIES,
        doors=(
            Door(
                tx=STAGE_W - 1,
                ty=_MID_Y,
                target_stage=1,
                target_spawn=(1 * TILE_SIZE, _MID_Y * TILE_SIZE),
            ),
        ),
        chapter_title="I. THE ENTRANCE",
    ),
    Stage(
        index=1,
        width=STAGE_W,
        height=STAGE_H,
        raw_map=_S1_MAP,
        default_spawn=(1 * TILE_SIZE, _MID_Y * TILE_SIZE),
        enemy_spawns=_S1_NORMAL,
        dash_spawns=_S1_DASH,
        doors=(
            Door(
                tx=STAGE_W - 1,
                ty=_MID_Y,
                target_stage=2,
                target_spawn=(1 * TILE_SIZE, _MID_Y * TILE_SIZE),
            ),
        ),
        switch_gates=(SwitchGate(switch=_S1_SWITCH, door=_S1_LOCKED),),
        chapter_title="II. THE MOSS HALL",
    ),
    Stage(
        index=2,
        width=STAGE_W,
        height=STAGE_H,
        raw_map=_S2_MAP,
        default_spawn=(1 * TILE_SIZE, _MID_Y * TILE_SIZE),
        enemy_spawns=(),
        dash_spawns=_S2_DASH,
        ranged_spawns=_S2_RANGED,
        doors=(
            Door(
                tx=STAGE_W - 1,
                ty=_MID_Y,
                target_stage=3,
                target_spawn=(1 * TILE_SIZE, _MID_Y * TILE_SIZE),
            ),
        ),
        chapter_title="III. THE DRIPPING CORRIDOR",
    ),
    Stage(
        index=3,
        width=STAGE_W,
        height=STAGE_H,
        raw_map=_S3_MAP,
        default_spawn=(1 * TILE_SIZE, _MID_Y * TILE_SIZE),
        enemy_spawns=_S3_NORMAL,
        tank_spawns=_S3_TANK,
        doors=(
            Door(
                tx=STAGE_W - 1,
                ty=_MID_Y,
                target_stage=4,
                target_spawn=((_S4_ENTRANCE[0] + 1) * TILE_SIZE, _S4_ENTRANCE[1] * TILE_SIZE),
            ),
        ),
        key_gates=(KeyGate(key=_S3_KEY, door=_S3_LOCKED),),
        chapter_title="IV. THE SPRING GATE",
    ),
    Stage(
        index=4,
        width=STAGE_W,
        height=STAGE_H,
        raw_map=_S4_MAP,
        default_spawn=((_S4_ENTRANCE[0] + 1) * TILE_SIZE, _S4_ENTRANCE[1] * TILE_SIZE),
        enemy_spawns=(),
        boss_spawn=(_S4_BOSS_TILE[0] * TILE_SIZE, _S4_BOSS_TILE[1] * TILE_SIZE),
        doors=(
            Door(
                tx=_S4_ENTRANCE[0],
                ty=_S4_ENTRANCE[1],
                target_stage=3,
                target_spawn=((STAGE_W - 2) * TILE_SIZE, _MID_Y * TILE_SIZE),
            ),
        ),
        chapter_title="V. THE CORE",
    ),
)
