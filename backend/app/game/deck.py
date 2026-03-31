from __future__ import annotations

import random

from .tile import Tile, build_full_tile_set


class Deck:
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self.tiles: list[Tile] = build_full_tile_set()
        self._rng.shuffle(self.tiles)

    @property
    def remaining(self) -> int:
        return len(self.tiles)

    def draw(self, count: int = 1) -> list[Tile]:
        if count <= 0:
            return []
        if count > len(self.tiles):
            raise ValueError("not enough tiles in deck")
        out = self.tiles[:count]
        self.tiles = self.tiles[count:]
        return out

