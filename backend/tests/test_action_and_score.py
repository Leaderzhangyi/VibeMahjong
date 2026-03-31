from app.game.action_checker import ActionChecker
from app.game.hand import Hand
from app.game.score_calculator import ScoreCalculator
from app.game.tile import Suit, Tile


def make_hand(codes: list[str]) -> Hand:
    return Hand([Tile.from_code(code) for code in codes])


def test_lack_rule_blocks_non_lack_discard() -> None:
    hand = make_hand(["1m", "2m", "3b", "3s"])
    assert ActionChecker.must_discard_lack(hand, Suit.WAN)
    assert not ActionChecker.can_discard(hand, Tile.from_code("3b"), Suit.WAN)
    assert ActionChecker.can_discard(hand, Tile.from_code("1m"), Suit.WAN)


def test_score_qing_yi_se_long_qi_dui_self_draw() -> None:
    hand_tiles = [
        Tile.from_code(code)
        for code in [
            "1m",
            "1m",
            "2m",
            "2m",
            "3m",
            "3m",
            "4m",
            "4m",
            "5m",
            "5m",
            "6m",
            "6m",
            "9m",
            "9m",
        ]
    ]
    result = ScoreCalculator.calculate_fan(hand_tiles=hand_tiles, self_draw=True, menqing=True)
    assert result.fan >= 9
    assert "qing_yi_se" in result.patterns
    assert "qi_dui" in result.patterns
    assert "zi_mo" in result.patterns

