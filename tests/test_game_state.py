import random
import unittest

from game_state import GameState


class TestGameState(unittest.TestCase):
    def test_seeded_rng_controls_start_and_first_goal(self) -> None:
        state1 = GameState(rows=8, cols=8, rng=random.Random(42))
        state2 = GameState(rows=8, cols=8, rng=random.Random(42))

        self.assertEqual(state1.snake, state2.snake)
        self.assertEqual(state1.goal, state2.goal)

    def test_seeded_rng_controls_following_goal_spawns(self) -> None:
        state1 = GameState(rows=6, cols=6, rng=random.Random(123))
        state2 = GameState(rows=6, cols=6, rng=random.Random(123))

        goals1 = [state1.goal]
        goals2 = [state2.goal]
        for _ in range(5):
            state1.spawn_goal()
            state2.spawn_goal()
            goals1.append(state1.goal)
            goals2.append(state2.goal)

        self.assertEqual(goals1, goals2)

    def test_step_out_of_bounds_sets_game_over(self) -> None:
        state = GameState(rows=3, cols=3, rng=random.Random(1))
        state.snake = [[0, 0]]
        moved = state.step(-1, 0)

        self.assertFalse(moved)
        self.assertTrue(state.state_over)

    def test_eat_goal_grows_snake_and_respawns_goal(self) -> None:
        state = GameState(rows=4, cols=4, rng=random.Random(9))
        state.snake = [[1, 1]]
        state.goal = (1, 2)

        moved = state.step(0, 1)

        self.assertTrue(moved)
        self.assertEqual(len(state.snake), 2)
        self.assertIsNotNone(state.goal)
        self.assertNotIn(list(state.goal), state.snake)

    def test_one_by_one_board_is_immediate_win(self) -> None:
        state = GameState(rows=1, cols=1, rng=random.Random(0))

        self.assertTrue(state.state_won)
        self.assertIsNone(state.goal)
        self.assertFalse(state.step(0, 1))


if __name__ == "__main__":
    unittest.main()
