"""
Headless simulation utilities for running automated Snake episodes without UI.
"""
from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
import random
import time
from typing import Callable

from game_state import GameState
from strategies import SnakeStrategy


@dataclass(frozen=True)
class SimulationResult:
    """Metrics collected from one simulation episode."""

    steps: int
    apples_eaten: int
    won: bool
    game_over: bool
    max_steps_reached: bool
    elapsed_ms: float


def run_episode(
    strategy: SnakeStrategy,
    rows: int = 6,
    cols: int = 6,
    max_steps: int = 1000,
    seed: int | None = None,
) -> SimulationResult:
    """Run one headless simulation and return summary metrics."""
    if seed is not None:
        random.seed(seed)

    state = GameState(rows=rows, cols=cols)
    initial_length = len(state.snake)
    steps = 0

    start = time.perf_counter()
    while not state.state_over and not state.state_won and steps < max_steps:
        delta_row, delta_col = strategy.get_next_direction(state)
        applied = state.step(delta_row, delta_col)
        steps += 1

        # Treat non-terminal invalid moves as failed episodes to avoid infinite loops.
        if not applied and not state.state_over and not state.state_won:
            state.state_over = True
            break

    elapsed_ms = (time.perf_counter() - start) * 1000.0
    apples_eaten = len(state.snake) - initial_length
    return SimulationResult(
        steps=steps,
        apples_eaten=apples_eaten,
        won=state.state_won,
        game_over=state.state_over,
        max_steps_reached=(not state.state_over and not state.state_won and steps >= max_steps),
        elapsed_ms=elapsed_ms,
    )


def run_batch(
    strategy_factory: Callable[[], SnakeStrategy],
    episodes: int = 1,
    rows: int = 6,
    cols: int = 6,
    max_steps: int = 1000,
    seed: int | None = None,
) -> list[SimulationResult]:
    """Run multiple episodes and return per-episode metrics."""
    seed_rng = random.Random(seed)
    results: list[SimulationResult] = []
    for _ in range(episodes):
        episode_seed = seed_rng.randrange(0, 2**32) if seed is not None else None
        result = run_episode(
            strategy=strategy_factory(),
            rows=rows,
            cols=cols,
            max_steps=max_steps,
            seed=episode_seed,
        )
        results.append(result)
    return results


def format_batch_summary(results: list[SimulationResult]) -> str:
    """Return a plain-text summary for a batch of simulation episodes."""
    if not results:
        return "No episodes were run."

    wins = sum(1 for r in results if r.won)
    game_overs = sum(1 for r in results if r.game_over)
    max_steps = sum(1 for r in results if r.max_steps_reached)

    avg_apples = mean(r.apples_eaten for r in results)
    avg_steps = mean(r.steps for r in results)
    avg_ms = mean(r.elapsed_ms for r in results)
    avg_decision_ms = mean((r.elapsed_ms / r.steps) if r.steps else 0.0 for r in results)

    return "\n".join(
        [
            f"Episodes: {len(results)}",
            f"Wins: {wins}",
            f"Game overs: {game_overs}",
            f"Reached max steps: {max_steps}",
            f"Average apples eaten: {avg_apples:.2f}",
            f"Average steps: {avg_steps:.2f}",
            f"Average episode runtime (ms): {avg_ms:.2f}",
            f"Average decision runtime (ms): {avg_decision_ms:.4f}",
        ]
    )
