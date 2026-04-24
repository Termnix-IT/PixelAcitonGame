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
class Stage:
    index: int
    width: int
    height: int
    raw_map: tuple[str, ...]
    default_spawn: tuple[int, int]
    enemy_spawns: tuple[tuple[int, int], ...]
    doors: tuple[Door, ...]

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


_MID_Y = STAGE_H // 2

# Stage 0 → east door leads to stage 1; stage 0 spawn is (2, 2).
# Stage 1 → west door leads back; stage 1 spawn is at center.
_S0_DOORS = ((STAGE_W - 1, _MID_Y),)
_S1_DOORS = ((0, _MID_Y),)

# Keep spawn and door-approach tiles open so neither is blocked by interior clumps.
_S0_SAFE = ((2, 2), (STAGE_W - 2, _MID_Y), (STAGE_W - 3, _MID_Y))
_S1_SAFE = ((STAGE_W // 2, _MID_Y), (1, _MID_Y), (2, _MID_Y))

_S0_MAP, _S0_ENEMIES = _generate(seed=1, doors=_S0_DOORS, safe_tiles=_S0_SAFE)
_S1_MAP, _S1_ENEMIES = _generate(seed=2, doors=_S1_DOORS, safe_tiles=_S1_SAFE)


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
    ),
    Stage(
        index=1,
        width=STAGE_W,
        height=STAGE_H,
        raw_map=_S1_MAP,
        default_spawn=((STAGE_W // 2) * TILE_SIZE, _MID_Y * TILE_SIZE),
        enemy_spawns=_S1_ENEMIES,
        doors=(
            Door(
                tx=0,
                ty=_MID_Y,
                target_stage=0,
                target_spawn=((STAGE_W - 2) * TILE_SIZE, _MID_Y * TILE_SIZE),
            ),
        ),
    ),
)
