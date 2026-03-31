from collections import Counter

from app.game.deck import Deck


def test_deck_has_108_tiles_and_27_unique_kinds() -> None:
    deck = Deck(seed=1)
    assert deck.remaining == 108
    codes = [tile.code for tile in deck.tiles]
    hist = Counter(codes)
    assert len(hist) == 27
    assert all(v == 4 for v in hist.values())


def test_draw_reduces_remaining() -> None:
    deck = Deck(seed=1)
    drawn = deck.draw(13)
    assert len(drawn) == 13
    assert deck.remaining == 95

