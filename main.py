"""
Entry point for running Snake in visual mode or headless simulation mode.
"""
from __future__ import annotations

import argparse

from simulation import format_batch_summary, run_batch
from strategies import (GreedyStrategy, HamiltonianStrategy, SnakeStrategy, BreadthFirstStrategy,
                        DepthFirstStrategy, AStarStrategy)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Snake game runner")
    parser.add_argument(
        "--mode",
        choices=["visual", "headless"],
        default="visual",
        help="Run tkinter UI (visual) or simulation-only (headless).",
    )
    parser.add_argument(
        "--strategy",
        choices=["manual", "greedy", "hamiltonian", "breadth", "depth", "astar"],
        default="manual",
        help="Movement controller. Manual is only valid in visual mode.",
    )
    parser.add_argument("--rows", type=int, default=8, help="Grid row count.")
    parser.add_argument("--cols", type=int, default=8, help="Grid column count.")
    parser.add_argument("--tick-ms", type=int, default=100, help="Visual tick interval in milliseconds.")
    parser.add_argument("--episodes", type=int, default=1, help="Headless: number of episodes to run.")
    parser.add_argument("--max-steps", type=int, default=1000, help="Headless: per-episode max steps.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for headless runs and visual play.")
    return parser.parse_args()


def _build_strategy(name: str) -> SnakeStrategy | None:
    if name == "manual":
        return None
    if name == "greedy":
        return GreedyStrategy()
    if name == "hamiltonian":
        return HamiltonianStrategy()
    if name == "breadth":
        return BreadthFirstStrategy()
    if name == "depth":
        return DepthFirstStrategy()
    if name == "astar":
        return AStarStrategy()
    raise ValueError(f"Unknown strategy: {name}")


def _validate_args(args: argparse.Namespace) -> None:
    if args.rows <= 0 or args.cols <= 0:
        raise ValueError("rows and cols must be positive integers")
    if args.tick_ms <= 0:
        raise ValueError("tick-ms must be a positive integer")
    if args.episodes <= 0:
        raise ValueError("episodes must be a positive integer")
    if args.max_steps <= 0:
        raise ValueError("max-steps must be a positive integer")
    if args.mode == "headless" and args.strategy == "manual":
        raise ValueError("manual strategy is not supported in headless mode")
    if args.strategy == "hamiltonian" and args.rows > 1 and args.cols > 1 and args.rows % 2 == 1 and args.cols % 2 == 1:
        raise ValueError("hamiltonian strategy requires at least one even grid dimension")


def _run_visual(args: argparse.Namespace) -> None:
    from snake_board import SnakeGame

    strategy = _build_strategy(args.strategy)

    game = SnakeGame(
        rows=args.rows,
        cols=args.cols,
        tick_ms=args.tick_ms,
        strategy=strategy,
        seed=args.seed,
    )
    game.mainloop()


def _run_headless(args: argparse.Namespace) -> None:
    def strategy_factory() -> SnakeStrategy:
        strategy = _build_strategy(args.strategy)
        assert strategy is not None
        return strategy

    results = run_batch(
        strategy_factory=strategy_factory,
        episodes=args.episodes,
        rows=args.rows,
        cols=args.cols,
        max_steps=args.max_steps,
        seed=args.seed,
    )
    print(format_batch_summary(results))


def main() -> None:
    args = _parse_args()
    try:
        _validate_args(args)
    except ValueError as exc:
        raise SystemExit(f"Error: {exc}") from exc

    if args.mode == "visual":
        _run_visual(args)
    else:
        _run_headless(args)


if __name__ == "__main__":
    main()
