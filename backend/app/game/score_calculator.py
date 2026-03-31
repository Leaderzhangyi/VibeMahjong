from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .tile import Tile
from .win_checker import WinChecker


@dataclass
class ScoreResult:
    fan: int
    patterns: list[str]


class ScoreCalculator:
    @staticmethod
    def calculate_fan(
        hand_tiles: list[Tile],
        melds: list[dict] | None = None,
        self_draw: bool = False,
        menqing: bool = True,
        kong_draw: bool = False,
        rob_kong: bool = False,
        kong_discard: bool = False,
    ) -> ScoreResult:
        if len(hand_tiles) != 14 or not WinChecker.is_win(hand_tiles):
            return ScoreResult(fan=0, patterns=[])

        melds = melds or []
        patterns: list[str] = []
        fan = 0

        counts = Counter(tile.code for tile in hand_tiles)
        is_qidui = WinChecker.is_seven_pairs(hand_tiles)
        is_long_qidui = is_qidui and any(c == 4 for c in counts.values())
        is_qingyise = len({tile.suit for tile in hand_tiles}) == 1
        is_duiduihu = (not is_qidui) and WinChecker.is_all_pungs(hand_tiles)

        if is_long_qidui:
            fan += 7
            patterns.append("long_qi_dui")
        elif is_qidui:
            fan += 3
            patterns.append("qi_dui")
        elif is_duiduihu:
            fan += 3
            patterns.append("dui_dui_hu")
        else:
            fan += 1
            patterns.append("ping_hu")

        if is_qingyise:
            fan += 5
            patterns.append("qing_yi_se")

        if self_draw:
            fan += 1
            patterns.append("zi_mo")

        if menqing and not melds:
            fan += 1
            patterns.append("men_qing")

        if kong_draw:
            fan += 1
            patterns.append("gang_shang_kai_hua")

        if rob_kong:
            fan += 1
            patterns.append("qiang_gang_hu")

        if kong_discard:
            fan += 1
            patterns.append("gang_shang_pao")

        return ScoreResult(fan=fan, patterns=patterns)

