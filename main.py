"""
Entry point for running Snake in visual mode or headless simulation mode.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime

from snake_board import ROWS, COLS

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
    parser.add_argument("--runall", type=int, default=0, help="If 1, ignores selected strategy and runs all. Must be in headless.")
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
    if args.mode == "headless" and args.strategy == "manual" and not args.runall == 1:
        raise ValueError("manual strategy is not supported in headless mode")
    if args.strategy == "hamiltonian" and args.rows > 1 and args.cols > 1 and args.rows % 2 == 1 and args.cols % 2 == 1:
        raise ValueError("hamiltonian strategy requires at least one even grid dimension")
    if args.runall == 1 and args.mode != "headless":
        raise ValueError("runall is only possible in headless")

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
    
    if args.runall == 1:
        strats = [GreedyStrategy(), HamiltonianStrategy(), BreadthFirstStrategy(),
                  DepthFirstStrategy(), AStarStrategy()]
    else:
        strats = [strategy_factory()]   

    results = run_batch(
        strategies=strats,
        episodes=args.episodes,
        rows=args.rows,
        cols=args.cols,
        max_steps=args.max_steps,
        seed=args.seed,
    )

    # Write to csv
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data_{timestamp}.csv"
    header = [[
        "Stragey",
        "Episodes",
        "Wins",
        "Game overs",
        "Reached max steps",
        "Average apples eaten",
        "Average steps",
        "Average episode runtime (ms)",
        "Average decision runtime (ms)",
    ]]
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(header)

    for r_set in results:
        print(format_batch_summary(r_set,filename))


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
