from __future__ import annotations

from dataclasses import dataclass

from app.game.game_room import GameRoom


@dataclass
class StepResult:
    observation: dict
    reward: float
    terminated: bool
    truncated: bool
    info: dict


class MahjongEnv:
    """Minimal Gym-like environment scaffold for RL training."""

    def __init__(self, seed: int | None = None) -> None:
        self.seed = seed
        self.room = GameRoom(room_id="rl-room", seed=seed)
        self.agent_sid = "agent"
        self.bot_sids = ["bot1", "bot2", "bot3"]
        self._setup_players()

    def reset(self) -> tuple[dict, dict]:
        self.room = GameRoom(room_id="rl-room", seed=self.seed)
        self._setup_players()
        for sid in [self.agent_sid, *self.bot_sids]:
            self.room.set_ready(sid, True)
        self._auto_to_playing()
        return self._observe(), {}

    def step(self, action: dict) -> StepResult:
        if self.room.phase == self.room.phase.GAME_OVER:
            return StepResult(self._observe(), 0.0, True, False, {"done": True})

        self._apply_agent_action(action)
        self._run_rule_bots()
        reward = self._calculate_reward()
        terminated = self.room.phase == self.room.phase.GAME_OVER
        return StepResult(self._observe(), reward, terminated, False, {})

    def action_mask(self) -> dict:
        seat = self.room.sid_to_seat[self.agent_sid]
        return self.room.available_actions(seat)

    def _setup_players(self) -> None:
        self.room.join(self.agent_sid, "agent")
        for sid in self.bot_sids:
            self.room.join(sid, sid)

    def _auto_to_playing(self) -> None:
        for sid in [self.agent_sid, *self.bot_sids]:
            if self.room.phase == self.room.phase.SWAP_TILES:
                hand = self.room._player_by_sid(sid).hand.to_codes()
                self.room.choose_swap_tiles(sid, hand[:3])
        for sid in [self.agent_sid, *self.bot_sids]:
            if self.room.phase == self.room.phase.CHOOSE_LACK:
                self.room.choose_lack(sid, "m")

    def _apply_agent_action(self, action: dict) -> None:
        name = action.get("action")
        if name == "discard":
            self.room.discard(self.agent_sid, action["tile"])
        elif name == "win":
            self.room.win(self.agent_sid, action.get("type", "self_draw"))
        elif name == "pass":
            self.room.pass_action(self.agent_sid)
        elif name == "kong":
            if action.get("type") == "concealed":
                self.room.kong_concealed(self.agent_sid, action["tile"])
            else:
                self.room.kong_exposed(self.agent_sid)
        elif name == "pong":
            self.room.pong(self.agent_sid)

    def _run_rule_bots(self) -> None:
        # MVP: random legal policy placeholder; replace with shanten/risk-aware policy.
        for sid in self.bot_sids:
            if self.room.phase != self.room.phase.PLAYING:
                return
            seat = self.room.sid_to_seat[sid]
            available = self.room.available_actions(seat)
            actions = available.get("actions", [])
            if not actions:
                continue
            if "win_self_draw" in actions:
                self.room.win(sid, "self_draw")
                continue
            if "win" in actions:
                self.room.win(sid, "discard")
                continue
            if "pass" in actions:
                self.room.pass_action(sid)
                continue
            if "discard" in actions:
                hand = self.room._player_by_sid(sid).hand.to_codes()
                self.room.discard(sid, hand[0])

    def _observe(self) -> dict:
        seat = self.room.sid_to_seat[self.agent_sid]
        snap = self.room.snapshot_for_sid(self.agent_sid)
        me = next(p for p in snap["players"] if p["seat"] == seat)
        return {
            "phase": snap["phase"],
            "hand": me.get("hand", []),
            "discards": {p["seat"]: p["discards"] for p in snap["players"]},
            "melds": {p["seat"]: p["melds"] for p in snap["players"]},
            "lack": me.get("lack"),
            "scores": {p["seat"]: p["score"] for p in snap["players"]},
            "available": snap["available"],
        }

    def _calculate_reward(self) -> float:
        if not self.room.result:
            return 0.0
        winner = self.room.result.winner
        if winner is None:
            return 0.0
        my_seat = self.room.sid_to_seat[self.agent_sid]
        if winner == my_seat:
            return float(self.room.result.fan * 10)
        return -5.0

