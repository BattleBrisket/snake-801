"""
Snake movement strategies: given GameState, return (delta_row, delta_col).
May use algors (pathfinding, distances) but contain no core path math themselves.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from algors import hamiltonian_cycle, manhattan_distance
from game_state import GameState


class SnakeStrategy(ABC):
    """Base class for movement strategies. State has .snake, .goal, .rows, .cols."""

    @abstractmethod
    def get_next_direction(self, state: GameState) -> tuple[int, int]:
        """Return (delta_row, delta_col) for the next move."""
        ...


class HamiltonianStrategy(SnakeStrategy):
    """Follow a Hamiltonian cycle so the snake eventually visits every cell. Path is computed once on first call."""

    def __init__(self) -> None:
        self._path: list[tuple[int, int]] | None = None

    def get_next_direction(self, state: GameState) -> tuple[int, int]:
        if self._path is None:
            head_row, head_col = state.snake[0][0], state.snake[0][1]
            self._path = hamiltonian_cycle(state.rows, state.cols, head_row, head_col)

        head_row, head_col = state.snake[0][0], state.snake[0][1]
        head = (head_row, head_col)
        for i, cell in enumerate(self._path):
            if cell == head:
                break
        else:
            return 0, 0  # fallback if head not in path
        next_i = (i + 1) % len(self._path)
        next_row, next_col = self._path[next_i]
        return next_row - head_row, next_col - head_col


class GreedyStrategy(SnakeStrategy):
    """Always move one step toward the goal (Manhattan distance). May trap itself."""

    def get_next_direction(self, state: GameState) -> tuple[int, int]:
        if not state.goal:
            return 0, 0
        head_row, head_col = state.snake[0][0], state.snake[0][1]
        goal_row, goal_col = state.goal
        best_delta_row, best_delta_col = 0, 0
        best_dist = manhattan_distance(head_row, head_col, goal_row, goal_col)
        for delta_row, delta_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = head_row + delta_row, head_col + delta_col
            if not (0 <= new_row < state.rows and 0 <= new_col < state.cols):
                continue
            if any(seg[0] == new_row and seg[1] == new_col for seg in state.snake[1:]):
                continue
            dist = manhattan_distance(new_row, new_col, goal_row, goal_col)
            if dist < best_dist:
                best_dist = dist
                best_delta_row, best_delta_col = delta_row, delta_col
        return best_delta_row, best_delta_col
