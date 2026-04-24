from __future__ import annotations

from typing import Protocol

import pyxel

from .assets import SOLID_TILES
from .config import TILE_SIZE
from .stage import Stage


class _TileSource(Protocol):
    def pget(self, x: int, y: int) -> tuple[int, int]: ...


class World:
    def __init__(self, stage: Stage, tilemap: _TileSource | None = None) -> None:
        if tilemap is None:
            tilemap = pyxel.tilemaps[stage.index]
        self._tm = tilemap
        self._tilemap_index = stage.index
        self.width = stage.width
        self.height = stage.height

    def is_solid_tile(self, tx: int, ty: int) -> bool:
        if tx < 0 or ty < 0 or tx >= self.width or ty >= self.height:
            return True
        return tuple(self._tm.pget(tx, ty)) in SOLID_TILES

    def rect_collides(self, x: float, y: float, w: int, h: int) -> bool:
        x0 = int(x // TILE_SIZE)
        y0 = int(y // TILE_SIZE)
        x1 = int((x + w - 1) // TILE_SIZE)
        y1 = int((y + h - 1) // TILE_SIZE)
        for ty in range(y0, y1 + 1):
            for tx in range(x0, x1 + 1):
                if self.is_solid_tile(tx, ty):
                    return True
        return False

    def draw(self) -> None:
        pyxel.bltm(0, 0, self._tilemap_index, 0, 0, self.width * TILE_SIZE, self.height * TILE_SIZE)
