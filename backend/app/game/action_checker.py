from __future__ import annotations

from dataclasses import dataclass

from .hand import Hand
from .tile import Suit, Tile
from .win_checker import WinChecker


@dataclass(frozen=True)
class KongOption:
    tile: Tile
    kong_type: str


class ActionChecker:
    @staticmethod
    def must_discard_lack(hand: Hand, lack: Suit | None) -> bool:
        if lack is None:
            return False
        return hand.suit_count(lack) > 0

    @staticmethod
    def can_discard(hand: Hand, tile: Tile, lack: Suit | None) -> bool:
        if ActionChecker.must_discard_lack(hand, lack) and tile.suit != lack:
            return False
        return hand.count(tile) > 0

    @staticmethod
    def can_pong(hand: Hand, tile: Tile, lack: Suit | None) -> bool:
        if ActionChecker.must_discard_lack(hand, lack):
            return False
        return hand.count(tile) >= 2

    @staticmethod
    def can_exposed_kong(hand: Hand, tile: Tile, lack: Suit | None) -> bool:
        if ActionChecker.must_discard_lack(hand, lack):
            return False
        return hand.count(tile) >= 3

    @staticmethod
    def concealed_kongs(hand: Hand, lack: Suit | None) -> list[KongOption]:
        if ActionChecker.must_discard_lack(hand, lack):
            return []
        out: list[KongOption] = []
        for code, count in hand.histogram().items():
            if count == 4:
                out.append(KongOption(tile=Tile.from_code(code), kong_type="concealed"))
        return out

    @staticmethod
    def can_win(hand: Hand, lack: Suit | None, winning_tile: Tile | None = None) -> bool:
        if ActionChecker.must_discard_lack(hand, lack):
            return False
        tiles = hand.tiles.copy()
        if winning_tile is not None:
            tiles.append(winning_tile)
        return WinChecker.is_win(tiles)

