import random
import unittest

from game_state import GameState
from strategies import GreedyStrategy, HamiltonianStrategy


class TestStrategies(unittest.TestCase):
    def test_greedy_moves_toward_goal_when_safe(self) -> None:
        state = GameState(rows=4, cols=4, rng=random.Random(5))
        state.snake = [[1, 1]]
        state.goal = (1, 3)

        direction = GreedyStrategy().get_next_direction(state)

        self.assertEqual(direction, (0, 1))

    def test_greedy_avoids_body_collision(self) -> None:
        state = GameState(rows=4, cols=4, rng=random.Random(5))
        state.snake = [[1, 1], [1, 2]]
        state.goal = (1, 2)

        direction = GreedyStrategy().get_next_direction(state)

        self.assertEqual(direction, (0, 0))

    def test_hamiltonian_returns_single_step_direction(self) -> None:
        state = GameState(rows=4, cols=4, rng=random.Random(3))
        strategy = HamiltonianStrategy()

        delta_row, delta_col = strategy.get_next_direction(state)

        self.assertEqual(abs(delta_row) + abs(delta_col), 1)

    def test_hamiltonian_raises_on_odd_by_odd_grid(self) -> None:
        state = GameState(rows=5, cols=5, rng=random.Random(3))
        strategy = HamiltonianStrategy()

        with self.assertRaises(ValueError):
            strategy.get_next_direction(state)


if __name__ == "__main__":
    unittest.main()
