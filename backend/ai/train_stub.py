from __future__ import annotations

import random

from ai.env import MahjongEnv


def random_policy_action(obs: dict) -> dict:
    available = obs["available"]["actions"]
    if "discard" in available and obs["hand"]:
        return {"action": "discard", "tile": random.choice(obs["hand"])}
    if "win_self_draw" in available:
        return {"action": "win", "type": "self_draw"}
    if "pass" in available:
        return {"action": "pass"}
    return {"action": "pass"}


def run_episode(steps: int = 200) -> float:
    env = MahjongEnv(seed=7)
    obs, _ = env.reset()
    total_reward = 0.0
    for _ in range(steps):
        action = random_policy_action(obs)
        result = env.step(action)
        obs = result.observation
        total_reward += result.reward
        if result.terminated or result.truncated:
            break
    return total_reward


if __name__ == "__main__":
    reward = run_episode()
    print(f"episode_reward={reward:.2f}")

