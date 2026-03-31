from app.game.tile import Tile
from app.game.win_checker import WinChecker


def make_tiles(codes: list[str]) -> list[Tile]:
    return [Tile.from_code(code) for code in codes]


def test_standard_win() -> None:
    tiles = make_tiles(
        [
            "1m",
            "2m",
            "3m",
            "3m",
            "4m",
            "5m",
            "6m",
            "7m",
            "8m",
            "2b",
            "2b",
            "2b",
            "5s",
            "5s",
        ]
    )
    assert WinChecker.is_standard_win(tiles)
    assert WinChecker.is_win(tiles)


def test_seven_pairs_win() -> None:
    tiles = make_tiles(
        [
            "1m",
            "1m",
            "2m",
            "2m",
            "3m",
            "3m",
            "4b",
            "4b",
            "5b",
            "5b",
            "6s",
            "6s",
            "7s",
            "7s",
        ]
    )
    assert WinChecker.is_seven_pairs(tiles)
    assert WinChecker.is_win(tiles)


def test_invalid_hand() -> None:
    tiles = make_tiles(
        [
            "1m",
            "1m",
            "1m",
            "2m",
            "2m",
            "2m",
            "3m",
            "3m",
            "3m",
            "4m",
            "4m",
            "4m",
            "5m",
            "7s",
        ]
    )
    assert not WinChecker.is_win(tiles)

