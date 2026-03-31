from app.game.game_room import GamePhase, GameRoom


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

