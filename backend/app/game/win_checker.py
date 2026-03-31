from __future__ import annotations

from collections import Counter
from functools import lru_cache

from .tile import Suit, Tile


class WinChecker:
    @staticmethod
    def is_seven_pairs(tiles: list[Tile]) -> bool:
        if len(tiles) != 14:
            return False
        counts = Counter(tile.code for tile in tiles)
        pair_units = 0
        for value in counts.values():
            if value not in (2, 4):
                return False
            pair_units += value // 2
        return pair_units == 7

    @staticmethod
    def is_standard_win(tiles: list[Tile]) -> bool:
        if len(tiles) % 3 != 2:
            return False
        counts = Counter(tile.code for tile in tiles)
        pair_candidates = [code for code, c in counts.items() if c >= 2]

        for pair_code in pair_candidates:
            temp = counts.copy()
            temp[pair_code] -= 2
            if temp[pair_code] == 0:
                del temp[pair_code]
            if WinChecker._all_suits_form_melds(temp):
                return True
        return False

    @staticmethod
    def is_win(tiles: list[Tile]) -> bool:
        return WinChecker.is_seven_pairs(tiles) or WinChecker.is_standard_win(tiles)

    @staticmethod
    def is_all_pungs(tiles: list[Tile]) -> bool:
        if len(tiles) != 14:
            return False
        counts = Counter(tile.code for tile in tiles)
        pair_candidates = [code for code, c in counts.items() if c >= 2]
        for pair_code in pair_candidates:
            temp = counts.copy()
            temp[pair_code] -= 2
            if temp[pair_code] == 0:
                del temp[pair_code]
            if all(v % 3 == 0 for v in temp.values()):
                return True
        return False

    @staticmethod
    def _all_suits_form_melds(counts: Counter[str]) -> bool:
        for suit in Suit:
            bucket = [0] * 10
            for rank in range(1, 10):
                code = f"{rank}{suit.value}"
                bucket[rank] = counts.get(code, 0)
            if not WinChecker._can_form_melds(tuple(bucket)):
                return False
        return True

    @staticmethod
    @lru_cache(maxsize=4096)
    def _can_form_melds(bucket: tuple[int, ...]) -> bool:
        mutable = list(bucket)
        idx = next((i for i in range(1, 10) if mutable[i] > 0), None)
        if idx is None:
            return True

        if mutable[idx] >= 3:
            mutable[idx] -= 3
            if WinChecker._can_form_melds(tuple(mutable)):
                return True
            mutable[idx] += 3

        if idx <= 7 and mutable[idx + 1] > 0 and mutable[idx + 2] > 0:
            mutable[idx] -= 1
            mutable[idx + 1] -= 1
            mutable[idx + 2] -= 1
            if WinChecker._can_form_melds(tuple(mutable)):
                return True

        return False

