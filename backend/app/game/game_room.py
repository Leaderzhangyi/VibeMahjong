from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum

from .action_checker import ActionChecker
from .deck import Deck
from .hand import Hand
from .score_calculator import ScoreCalculator
from .tile import Suit, Tile


class GamePhase(str, Enum):
    WAITING = "WAITING"
    SWAP_TILES = "SWAP_TILES"
    CHOOSE_LACK = "CHOOSE_LACK"
    PLAYING = "PLAYING"
    GAME_OVER = "GAME_OVER"


class SwapDirection(str, Enum):
    CLOCKWISE = "clockwise"
    COUNTERCLOCKWISE = "counterclockwise"
    OPPOSITE = "opposite"


@dataclass
class PlayerState:
    sid: str
    seat: int
    name: str
    hand: Hand = field(default_factory=Hand)
    discards: list[Tile] = field(default_factory=list)
    melds: list[dict] = field(default_factory=list)
    score: int = 0
    ready: bool = False
    lack: Suit | None = None
    swap_selection: list[Tile] | None = None
    last_action: str | None = None


@dataclass
class ReactionContext:
    tile: Tile
    from_seat: int
    candidates: dict[int, set[str]]
    passed: set[int] = field(default_factory=set)


@dataclass
class RoundResult:
    winner: int | None
    win_type: str
    fan: int
    patterns: list[str]
    payments: dict[int, int]


class GameRoom:
    BOT_SID_PREFIX = "bot:"

    def __init__(self, room_id: str, seed: int | None = None, auto_fill_bots: bool = False) -> None:
        self.room_id = room_id
        self.seed = seed
        self.auto_fill_bots = auto_fill_bots
        self.phase: GamePhase = GamePhase.WAITING
        self.players: list[PlayerState | None] = [None, None, None, None]
        self.sid_to_seat: dict[str, int] = {}
        self.dealer_seat = 0
        self.current_turn: int | None = None
        self.swap_direction: SwapDirection | None = None
        self.deck: Deck | None = None
        self.last_discard: Tile | None = None
        self.last_discard_seat: int | None = None
        self.reaction: ReactionContext | None = None
        self.result: RoundResult | None = None
        self.last_kong_seat: int | None = None

    def join(self, sid: str, name: str) -> int:
        if sid in self.sid_to_seat:
            return self.sid_to_seat[sid]
        for seat in range(4):
            if self.players[seat] is None:
                self.players[seat] = PlayerState(sid=sid, seat=seat, name=name)
                self.sid_to_seat[sid] = seat
                return seat
        raise ValueError("room is full")

    def leave(self, sid: str) -> None:
        seat = self.sid_to_seat.pop(sid, None)
        if seat is None:
            return
        self.players[seat] = None
        if not self._is_bot_sid(sid):
            for idx, player in enumerate(self.players):
                if player and self._is_bot_sid(player.sid):
                    self.sid_to_seat.pop(player.sid, None)
                    self.players[idx] = None
        self.phase = GamePhase.WAITING
        self.current_turn = None
        self.reaction = None

    def set_ready(self, sid: str, ready: bool) -> None:
        player = self._player_by_sid(sid)
        player.ready = ready
        if ready and self._active_player_count() == 4 and all(self.players[i] and self.players[i].ready for i in range(4)):
            self.start_round()
        if self.auto_fill_bots:
            self.auto_progress()

    def start_round(self) -> None:
        self.phase = GamePhase.SWAP_TILES
        self.deck = Deck(seed=self.seed)
        self.current_turn = self.dealer_seat
        self.last_discard = None
        self.last_discard_seat = None
        self.reaction = None
        self.result = None
        self.last_kong_seat = None
        self.swap_direction = random.choice(list(SwapDirection))

        for player in self._iter_players():
            player.hand = Hand()
            player.discards = []
            player.melds = []
            player.lack = None
            player.swap_selection = None
            player.last_action = None

        for _ in range(13):
            for seat in range(4):
                player = self._player_by_seat(seat)
                player.hand.add(self._draw_one())
        self._player_by_seat(self.dealer_seat).hand.add(self._draw_one())

    def choose_swap_tiles(self, sid: str, tile_codes: list[str]) -> None:
        if self.phase != GamePhase.SWAP_TILES:
            raise ValueError("not in swap phase")
        if len(tile_codes) != 3:
            raise ValueError("must choose exactly 3 tiles")
        player = self._player_by_sid(sid)
        selected = [Tile.from_code(c) for c in tile_codes]
        temp = player.hand.tiles.copy()
        for tile in selected:
            if tile not in temp:
                raise ValueError(f"tile not in hand: {tile.code}")
            temp.remove(tile)
        player.swap_selection = selected

        if all(p and p.swap_selection for p in self.players):
            self._apply_swap()
            self.phase = GamePhase.CHOOSE_LACK

    def choose_lack(self, sid: str, suit_value: str) -> None:
        if self.phase != GamePhase.CHOOSE_LACK:
            raise ValueError("not in choose lack phase")
        player = self._player_by_sid(sid)
        player.lack = Suit(suit_value)
        if all(p and p.lack is not None for p in self.players):
            self.phase = GamePhase.PLAYING
            self.current_turn = self.dealer_seat

    def discard(self, sid: str, tile_code: str) -> None:
        if self.phase != GamePhase.PLAYING:
            raise ValueError("not in playing phase")
        if self.reaction is not None:
            raise ValueError("waiting for reactions")
        seat = self._seat_by_sid(sid)
        if seat != self.current_turn:
            raise ValueError("not your turn")
        player = self._player_by_seat(seat)
        tile = Tile.from_code(tile_code)
        if len(player.hand.tiles) % 3 != 2:
            raise ValueError("hand tile count does not allow discard")
        must_lack = ActionChecker.must_discard_lack(player.hand, player.lack)
        if must_lack and player.lack is not None and tile.suit != player.lack:
            raise ValueError(f"must discard lack suit first: {player.lack.value}")
        if player.hand.count(tile) <= 0:
            raise ValueError("tile not in hand")
        if not ActionChecker.can_discard(player.hand, tile, player.lack):
            raise ValueError("illegal discard")

        player.hand.remove(tile)
        player.discards.append(tile)
        player.last_action = f"discard:{tile.code}"
        self.last_discard = tile
        self.last_discard_seat = seat
        self.last_kong_seat = None

        candidates: dict[int, set[str]] = {}
        for other in self._iter_players():
            if other.seat == seat:
                continue
            options: set[str] = set()
            if ActionChecker.can_win(other.hand, other.lack, winning_tile=tile):
                options.add("win")
            if ActionChecker.can_pong(other.hand, tile, other.lack):
                options.add("pong")
            if ActionChecker.can_exposed_kong(other.hand, tile, other.lack):
                options.add("kong_exposed")
            if options:
                candidates[other.seat] = options

        if candidates:
            self.reaction = ReactionContext(tile=tile, from_seat=seat, candidates=candidates)
            self.current_turn = None
        else:
            self._advance_turn_after_discard()

    def pass_action(self, sid: str) -> None:
        if self.reaction is None:
            raise ValueError("no action to pass")
        seat = self._seat_by_sid(sid)
        if seat not in self.reaction.candidates:
            raise ValueError("you have no pending action")
        self.reaction.passed.add(seat)
        if self.reaction.passed >= set(self.reaction.candidates.keys()):
            self.reaction = None
            self._advance_turn_after_discard()

    def pong(self, sid: str) -> None:
        reaction = self._require_reaction()
        seat = self._seat_by_sid(sid)
        if seat not in reaction.candidates or "pong" not in reaction.candidates[seat]:
            raise ValueError("pong unavailable")
        if self._exists_unpassed_higher_priority_win(except_seat=seat):
            raise ValueError("win has priority; wait for other players")

        player = self._player_by_seat(seat)
        player.hand.remove(reaction.tile)
        player.hand.remove(reaction.tile)
        player.melds.append({"type": "pong", "tiles": [reaction.tile.code] * 3, "from": reaction.from_seat})
        player.last_action = f"pong:{reaction.tile.code}"
        self.reaction = None
        self.current_turn = seat
        self.last_discard = None
        self.last_discard_seat = None

    def kong_exposed(self, sid: str) -> None:
        reaction = self._require_reaction()
        seat = self._seat_by_sid(sid)
        if seat not in reaction.candidates or "kong_exposed" not in reaction.candidates[seat]:
            raise ValueError("kong unavailable")
        if self._exists_unpassed_higher_priority_win(except_seat=seat):
            raise ValueError("win has priority; wait for other players")

        player = self._player_by_seat(seat)
        for _ in range(3):
            player.hand.remove(reaction.tile)
        player.melds.append({"type": "kong_exposed", "tiles": [reaction.tile.code] * 4, "from": reaction.from_seat})
        player.last_action = f"kong_exposed:{reaction.tile.code}"
        self._apply_kong_score(seat=seat, from_seat=reaction.from_seat, concealed=False)
        self.reaction = None
        self.current_turn = seat
        self.last_discard = None
        self.last_discard_seat = None
        self.last_kong_seat = seat
        player.hand.add(self._draw_one())

    def kong_concealed(self, sid: str, tile_code: str) -> None:
        if self.phase != GamePhase.PLAYING:
            raise ValueError("not in playing phase")
        if self.reaction is not None:
            raise ValueError("waiting for reactions")
        seat = self._seat_by_sid(sid)
        if seat != self.current_turn:
            raise ValueError("not your turn")
        player = self._player_by_seat(seat)
        tile = Tile.from_code(tile_code)
        options = ActionChecker.concealed_kongs(player.hand, player.lack)
        if tile.code not in {opt.tile.code for opt in options}:
            raise ValueError("concealed kong unavailable")

        for _ in range(4):
            player.hand.remove(tile)
        player.melds.append({"type": "kong_concealed", "tiles": [tile.code] * 4, "from": seat})
        player.last_action = f"kong_concealed:{tile.code}"
        self._apply_kong_score(seat=seat, from_seat=None, concealed=True)
        self.last_kong_seat = seat
        player.hand.add(self._draw_one())

    def win(self, sid: str, win_type: str) -> None:
        seat = self._seat_by_sid(sid)
        if win_type == "self_draw":
            self._win_self_draw(seat)
            return
        if win_type != "discard":
            raise ValueError("invalid win type")
        reaction = self._require_reaction()
        if seat not in reaction.candidates or "win" not in reaction.candidates[seat]:
            raise ValueError("discard win unavailable")

        winner = self._player_by_seat(seat)
        final_tiles = winner.hand.tiles + [reaction.tile]
        score = ScoreCalculator.calculate_fan(
            hand_tiles=final_tiles,
            melds=winner.melds,
            self_draw=False,
            menqing=len(winner.melds) == 0,
            kong_discard=self.last_kong_seat == reaction.from_seat,
        )
        if score.fan <= 0:
            raise ValueError("hand is not a winning hand")
        self._apply_round_score_discard_win(winner_seat=seat, from_seat=reaction.from_seat, fan=score.fan)
        self.result = RoundResult(
            winner=seat,
            win_type="discard",
            fan=score.fan,
            patterns=score.patterns,
            payments={i: self._player_by_seat(i).score for i in range(4)},
        )
        self.phase = GamePhase.GAME_OVER
        self.reaction = None
        self.current_turn = None

    def available_actions(self, seat: int) -> dict:
        actions: dict = {"actions": []}
        player = self._player_by_seat(seat)
        if self.phase != GamePhase.PLAYING:
            return actions
        if self.reaction and seat in self.reaction.candidates and seat not in self.reaction.passed:
            actions["actions"] = sorted(self.reaction.candidates[seat]) + ["pass"]
            actions["target_tile"] = self.reaction.tile.code
            return actions
        if seat != self.current_turn:
            return actions

        actions["actions"].append("discard")
        if ActionChecker.can_win(player.hand, player.lack):
            actions["actions"].append("win_self_draw")
        kongs = ActionChecker.concealed_kongs(player.hand, player.lack)
        if kongs:
            actions["actions"].append("kong_concealed")
            actions["concealed_kong_tiles"] = [opt.tile.code for opt in kongs]
        return actions

    def snapshot_for_sid(self, sid: str) -> dict:
        seat = self._seat_by_sid(sid)
        payload = {
            "room_id": self.room_id,
            "phase": self.phase.value,
            "dealer_seat": self.dealer_seat,
            "current_turn": self.current_turn,
            "swap_direction": self.swap_direction.value if self.swap_direction else None,
            "deck_remaining": self.deck.remaining if self.deck else 0,
            "last_discard": self.last_discard.code if self.last_discard else None,
            "last_discard_seat": self.last_discard_seat,
            "players": [],
            "me": seat,
            "available": self.available_actions(seat),
            "result": self.result.__dict__ if self.result else None,
        }
        for player in self._iter_players():
            item = {
                "seat": player.seat,
                "name": player.name,
                "is_bot": self._is_bot_sid(player.sid),
                "ready": player.ready,
                "score": player.score,
                "lack": player.lack.value if player.lack else None,
                "tile_count": len(player.hand.tiles),
                "discards": [t.code for t in player.discards],
                "melds": player.melds,
                "last_action": player.last_action,
            }
            if player.seat == seat:
                item["hand"] = player.hand.to_codes(sorted_output=True)
            payload["players"].append(item)
        return payload

    def _win_self_draw(self, seat: int) -> None:
        if self.phase != GamePhase.PLAYING:
            raise ValueError("not in playing phase")
        if seat != self.current_turn:
            raise ValueError("not your turn")
        player = self._player_by_seat(seat)
        score = ScoreCalculator.calculate_fan(
            hand_tiles=player.hand.tiles.copy(),
            melds=player.melds,
            self_draw=True,
            menqing=len(player.melds) == 0,
            kong_draw=self.last_kong_seat == seat,
        )
        if score.fan <= 0:
            raise ValueError("hand is not a winning hand")
        self._apply_round_score_self_draw(winner_seat=seat, fan=score.fan)
        self.result = RoundResult(
            winner=seat,
            win_type="self_draw",
            fan=score.fan,
            patterns=score.patterns,
            payments={i: self._player_by_seat(i).score for i in range(4)},
        )
        self.phase = GamePhase.GAME_OVER
        self.current_turn = None

    def _apply_swap(self) -> None:
        direction = self.swap_direction
        if direction is None:
            raise ValueError("swap direction missing")

        sends: dict[int, list[Tile]] = {}
        for player in self._iter_players():
            assert player.swap_selection is not None
            sends[player.seat] = player.swap_selection
            for tile in player.swap_selection:
                player.hand.remove(tile)

        for seat in range(4):
            receive_from = self._swap_from_seat(seat, direction)
            self._player_by_seat(seat).hand.add_many(sends[receive_from])

    def _swap_from_seat(self, target_seat: int, direction: SwapDirection) -> int:
        if direction == SwapDirection.CLOCKWISE:
            return (target_seat - 1) % 4
        if direction == SwapDirection.COUNTERCLOCKWISE:
            return (target_seat + 1) % 4
        return (target_seat + 2) % 4

    def _advance_turn_after_discard(self) -> None:
        if self.last_discard_seat is None:
            raise ValueError("missing discard seat")
        next_seat = (self.last_discard_seat + 1) % 4
        self.current_turn = next_seat
        player = self._player_by_seat(next_seat)
        drawn = self._safe_draw_one()
        if drawn is None:
            self.phase = GamePhase.GAME_OVER
            self.result = RoundResult(winner=None, win_type="draw", fan=0, patterns=["draw"], payments={i: self._player_by_seat(i).score for i in range(4)})
            self.current_turn = None
            return
        player.hand.add(drawn)
        player.last_action = f"draw:{drawn.code}"

    def _apply_round_score_self_draw(self, winner_seat: int, fan: int) -> None:
        winner = self._player_by_seat(winner_seat)
        gain = fan * 3
        winner.score += gain
        for seat in range(4):
            if seat == winner_seat:
                continue
            self._player_by_seat(seat).score -= fan

    def _apply_round_score_discard_win(self, winner_seat: int, from_seat: int, fan: int) -> None:
        winner = self._player_by_seat(winner_seat)
        lose = fan * 3
        winner.score += lose
        self._player_by_seat(from_seat).score -= lose

    def _apply_kong_score(self, seat: int, from_seat: int | None, concealed: bool) -> None:
        value = 2 if concealed else 1
        player = self._player_by_seat(seat)
        if from_seat is not None:
            self._player_by_seat(from_seat).score -= value * 3
            player.score += value * 3
            return
        for idx in range(4):
            if idx == seat:
                continue
            self._player_by_seat(idx).score -= value
            player.score += value

    def _exists_unpassed_higher_priority_win(self, except_seat: int) -> bool:
        reaction = self._require_reaction()
        for seat, options in reaction.candidates.items():
            if seat == except_seat:
                continue
            if seat in reaction.passed:
                continue
            if "win" in options:
                return True
        return False

    def _require_reaction(self) -> ReactionContext:
        if self.reaction is None:
            raise ValueError("no pending reaction")
        return self.reaction

    def _draw_one(self) -> Tile:
        if self.deck is None:
            raise ValueError("deck is not initialized")
        return self.deck.draw(1)[0]

    def _safe_draw_one(self) -> Tile | None:
        if self.deck is None:
            return None
        if self.deck.remaining <= 0:
            return None
        return self.deck.draw(1)[0]

    def _active_player_count(self) -> int:
        return len([p for p in self.players if p is not None])

    def human_player_count(self) -> int:
        return len([p for p in self.players if p is not None and not self._is_bot_sid(p.sid)])

    def auto_progress(self, max_steps: int = 256) -> None:
        for _ in range(max_steps):
            progressed = False

            if self.phase == GamePhase.WAITING and self.auto_fill_bots:
                self._fill_empty_with_bots_if_needed()
                if self._active_player_count() == 4 and all(self.players[i] and self.players[i].ready for i in range(4)):
                    self.start_round()
                    progressed = True

            elif self.phase == GamePhase.SWAP_TILES:
                for player in self._iter_players():
                    if not self._is_bot_sid(player.sid):
                        continue
                    if player.swap_selection is not None:
                        continue
                    choice = player.hand.to_codes(sorted_output=True)[:3]
                    self.choose_swap_tiles(player.sid, choice)
                    progressed = True

            elif self.phase == GamePhase.CHOOSE_LACK:
                for player in self._iter_players():
                    if not self._is_bot_sid(player.sid):
                        continue
                    if player.lack is not None:
                        continue
                    suit = self._bot_choose_lack(player)
                    self.choose_lack(player.sid, suit.value)
                    progressed = True

            elif self.phase == GamePhase.PLAYING:
                if self.reaction is not None:
                    for seat in list(self.reaction.candidates.keys()):
                        if seat in self.reaction.passed:
                            continue
                        player = self._player_by_seat(seat)
                        if not self._is_bot_sid(player.sid):
                            continue
                        options = self.reaction.candidates[seat]
                        if "win" in options and not self._has_pending_human_reaction():
                            self.win(player.sid, "discard")
                            progressed = True
                            break
                        self.pass_action(player.sid)
                        progressed = True
                    if progressed:
                        continue

                if self.current_turn is not None:
                    player = self._player_by_seat(self.current_turn)
                    if self._is_bot_sid(player.sid):
                        available = self.available_actions(player.seat)
                        actions = available.get("actions", [])
                        if "win_self_draw" in actions:
                            self.win(player.sid, "self_draw")
                            progressed = True
                        elif "kong_concealed" in actions:
                            kong_tiles = available.get("concealed_kong_tiles", [])
                            if kong_tiles:
                                self.kong_concealed(player.sid, kong_tiles[0])
                                progressed = True
                        elif "discard" in actions:
                            tile = self._bot_choose_discard(player)
                            self.discard(player.sid, tile.code)
                            progressed = True

            if not progressed:
                break

    def _iter_players(self) -> list[PlayerState]:
        return [p for p in self.players if p is not None]

    def _fill_empty_with_bots_if_needed(self) -> None:
        if not any(p and p.ready and not self._is_bot_sid(p.sid) for p in self.players):
            return
        for seat in range(4):
            player = self.players[seat]
            if player is None:
                sid = f"{self.BOT_SID_PREFIX}{self.room_id}:{seat}"
                bot = PlayerState(sid=sid, seat=seat, name=f"Bot{seat}", ready=True)
                self.players[seat] = bot
                self.sid_to_seat[sid] = seat
            elif self._is_bot_sid(player.sid):
                player.ready = True

    def _bot_choose_lack(self, player: PlayerState) -> Suit:
        counts = {suit: player.hand.suit_count(suit) for suit in Suit}
        return min(Suit, key=lambda s: (counts[s], s.value))

    def _bot_choose_discard(self, player: PlayerState) -> Tile:
        sorted_hand = player.hand.sorted()
        if player.lack is not None:
            lack_tiles = [tile for tile in sorted_hand if tile.suit == player.lack]
            if lack_tiles:
                return lack_tiles[0]
        return sorted_hand[0]

    def _has_pending_human_reaction(self) -> bool:
        if self.reaction is None:
            return False
        for seat in self.reaction.candidates.keys():
            if seat in self.reaction.passed:
                continue
            player = self._player_by_seat(seat)
            if not self._is_bot_sid(player.sid):
                return True
        return False

    def _is_bot_sid(self, sid: str) -> bool:
        return sid.startswith(self.BOT_SID_PREFIX)

    def _player_by_sid(self, sid: str) -> PlayerState:
        return self._player_by_seat(self._seat_by_sid(sid))

    def _seat_by_sid(self, sid: str) -> int:
        if sid not in self.sid_to_seat:
            raise ValueError("player not in room")
        return self.sid_to_seat[sid]

    def _player_by_seat(self, seat: int) -> PlayerState:
        player = self.players[seat]
        if player is None:
            raise ValueError(f"seat {seat} is empty")
        return player


class GameService:
    def __init__(self) -> None:
        self.rooms: dict[str, GameRoom] = {}

    def get_or_create_room(self, room_id: str) -> GameRoom:
        if room_id not in self.rooms:
            self.rooms[room_id] = GameRoom(room_id=room_id, auto_fill_bots=True)
        return self.rooms[room_id]

    def maybe_cleanup_room(self, room_id: str) -> None:
        room = self.rooms.get(room_id)
        if not room:
            return
        if room.human_player_count() == 0:
            del self.rooms[room_id]
