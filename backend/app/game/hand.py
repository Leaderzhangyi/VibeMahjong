from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from .tile import Suit, Tile, sorted_tiles


@dataclass
class Hand:
    tiles: list[Tile] = field(default_factory=list)

    def sorted(self) -> list[Tile]:
        return sorted_tiles(self.tiles)

    def add(self, tile: Tile) -> None:
        self.tiles.append(tile)

    def add_many(self, tiles: list[Tile]) -> None:
        self.tiles.extend(tiles)

    def remove(self, tile: Tile) -> None:
        for idx, t in enumerate(self.tiles):
            if t == tile:
                self.tiles.pop(idx)
                return
        raise ValueError(f"tile not in hand: {tile.code}")

    def remove_code(self, code: str, count: int = 1) -> None:
        for _ in range(count):
            tile = Tile.from_code(code)
            self.remove(tile)

    def count(self, tile: Tile) -> int:
        return sum(1 for t in self.tiles if t == tile)

    def count_code(self, code: str) -> int:
        tile = Tile.from_code(code)
        return self.count(tile)

    def suit_count(self, suit: Suit) -> int:
        return sum(1 for t in self.tiles if t.suit == suit)

    def to_codes(self, sorted_output: bool = True) -> list[str]:
        data = self.sorted() if sorted_output else self.tiles
        return [tile.code for tile in data]

    def histogram(self) -> Counter[str]:
        return Counter(tile.code for tile in self.tiles)

