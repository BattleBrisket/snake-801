"""
Entry point: run the snake game. Use manual play or pass a strategy.
"""
from snake_board import SnakeGame
from strategies import HamiltonianStrategy


def main() -> None:
    game = SnakeGame(
        # rows=6, cols=6, tick_ms=100,  # optional; defaults shown
        strategy=None,  # None = arrow keys; or HamiltonianStrategy(), GreedyStrategy(), etc.
    )
    game.mainloop()


if __name__ == "__main__":
    main()
