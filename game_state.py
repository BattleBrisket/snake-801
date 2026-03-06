"""
Game state and rules only. No UI. Used by SnakeGame and strategies.
"""
from __future__ import annotations

import random


class GameState:
    """Holds snake position, goal, and game rules. No drawing."""

    def __init__(self, rows: int = 6, cols: int = 6, rng: random.Random | None = None):
        self.rows = rows
        self.cols = cols
        self._rng = rng if rng is not None else random.Random()
        start_row = self._rng.randrange(rows)
        start_col = self._rng.randrange(cols)
        self.snake = [[start_row, start_col]]  # [row, col] per segment; index 0 is head
        self.direction = (1, 0)  # (dr, dc); image default is down
        self.goal: tuple[int, int] | None = None  # (row, col)
        self.state_over = False
        self.state_won = False
        self.path = []
        if len(self.snake) == self.rows * self.cols:
            self.state_won = True
        else:
            self.spawn_goal()

    def spawn_goal(self) -> None:
        """Pick a random cell not occupied by the snake and set it as the goal."""
        empty_cells = [
            (row, col)
            for row in range(self.rows)
            for col in range(self.cols)
            if [row, col] not in self.snake
        ]
        if not empty_cells:
            self.goal = None
            return
        self.goal = self._rng.choice(empty_cells)

    def step(self, delta_row: int, delta_col: int) -> bool:
        """
        Apply one move in direction (delta_row, delta_col). Returns True if the move was applied.
        Sets state_over / state_won and returns False if the move is invalid or game ended.
        """
        if self.state_over or self.state_won:
            return False

        current_head_row, current_head_col = self.snake[0][0], self.snake[0][1]
        next_head_row = current_head_row + delta_row
        next_head_col = current_head_col + delta_col

        if not (0 <= next_head_row < self.rows and 0 <= next_head_col < self.cols):
            self.state_over = True
            return False

        for i in range(1, len(self.snake)):
            if self.snake[i][0] == next_head_row and self.snake[i][1] == next_head_col:
                self.state_over = True
                return False

        tail_row, tail_col = self.snake[-1][0], self.snake[-1][1]

        for i in range(len(self.snake) - 1, 0, -1):
            self.snake[i][0] = self.snake[i - 1][0]
            self.snake[i][1] = self.snake[i - 1][1]
        self.snake[0][0] = next_head_row
        self.snake[0][1] = next_head_col

        if self.goal and (next_head_row, next_head_col) == self.goal:
            self.snake.append([tail_row, tail_col])
            if len(self.snake) == self.rows * self.cols:
                self.state_won = True
            else:
                self.spawn_goal()

        self.direction = (delta_row, delta_col)
        return True
