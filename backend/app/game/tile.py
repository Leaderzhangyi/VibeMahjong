from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Suit(str, Enum):
    WAN = "m"
    TONG = "b"
    TIAO = "s"


SUIT_ORDER: dict[Suit, int] = {
    Suit.WAN: 0,
    Suit.TONG: 1,
    Suit.TIAO: 2,
}


@dataclass(frozen=True)
class Tile:
    suit: Suit
    rank: int

    def __post_init__(self) -> None:
        if self.rank < 1 or self.rank > 9:
            raise ValueError(f"rank out of range: {self.rank}")

    @property
    def code(self) -> str:
        return f"{self.rank}{self.suit.value}"

    @staticmethod
    def from_code(code: str) -> "Tile":
        if len(code) != 2:
            raise ValueError(f"invalid tile code: {code}")
        rank = int(code[0])
        suit = Suit(code[1])
        return Tile(suit=suit, rank=rank)

    def sort_key(self) -> tuple[int, int]:
        return SUIT_ORDER[self.suit], self.rank


def sorted_tiles(tiles: list[Tile]) -> list[Tile]:
    return sorted(tiles, key=lambda t: t.sort_key())


def build_full_tile_set() -> list[Tile]:
    tiles: list[Tile] = []
    for suit in Suit:
        for rank in range(1, 10):
            for _ in range(4):
                tiles.append(Tile(suit=suit, rank=rank))
    return tiles

