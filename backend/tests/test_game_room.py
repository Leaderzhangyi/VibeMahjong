import pytest

from app.game.game_room import GamePhase, GameRoom
from app.game.hand import Hand
from app.game.tile import Tile


def setup_full_room() -> GameRoom:
    room = GameRoom("r1", seed=42)
    for i in range(4):
        sid = f"s{i}"
        room.join(sid=sid, name=f"p{i}")
        room.set_ready(sid=sid, ready=True)
    return room


def test_ready_starts_round() -> None:
    room = setup_full_room()
    assert room.phase == GamePhase.SWAP_TILES
    assert room.current_turn == 0


def test_swap_and_choose_lack_transitions() -> None:
    room = setup_full_room()
    for i in range(4):
        sid = f"s{i}"
        hand_codes = room._player_by_sid(sid).hand.to_codes()
        room.choose_swap_tiles(sid=sid, tile_codes=hand_codes[:3])
    assert room.phase == GamePhase.CHOOSE_LACK
    for i in range(4):
        room.choose_lack(sid=f"s{i}", suit_value="m")
    assert room.phase == GamePhase.PLAYING


def test_single_player_ready_auto_fills_bots() -> None:
    room = GameRoom("solo", seed=7, auto_fill_bots=True)
    room.join("human-1", "human")
    room.set_ready("human-1", True)
    assert room.phase == GamePhase.SWAP_TILES
    assert room._active_player_count() == 4

    hand_codes = room._player_by_sid("human-1").hand.to_codes()
    room.choose_swap_tiles("human-1", hand_codes[:3])
    room.auto_progress()
    assert room.phase == GamePhase.CHOOSE_LACK

    room.choose_lack("human-1", "m")
    room.auto_progress()
    assert room.phase == GamePhase.PLAYING


def test_discard_non_lack_tile_returns_clear_error() -> None:
    room = setup_full_room()
    for i in range(4):
        sid = f"s{i}"
        hand_codes = room._player_by_sid(sid).hand.to_codes()
        room.choose_swap_tiles(sid=sid, tile_codes=hand_codes[:3])
    for i in range(4):
        room.choose_lack(sid=f"s{i}", suit_value="m")
    assert room.phase == GamePhase.PLAYING

    room._player_by_sid("s0").hand = Hand([Tile.from_code(c) for c in ["1m", "2b", "2b", "3b", "3b", "4s", "4s", "5s", "5s", "6s", "6s", "7s", "7s", "8s"]])
    with pytest.raises(ValueError, match="must discard lack suit first"):
        room.discard("s0", "2b")
