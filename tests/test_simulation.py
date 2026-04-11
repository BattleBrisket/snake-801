import unittest

from simulation import SimulationResult, format_batch_summary, run_batch, run_episode
from strategies import GreedyStrategy, HamiltonianStrategy, BreadthFirstStrategy, DepthFirstStrategy, AStarStrategy


def _stable_fields(result: SimulationResult) -> tuple[int, int, bool, bool, bool]:
    return (
        result.steps,
        result.apples_eaten,
        result.won,
        result.game_over,
        result.max_steps_reached,
    )


class TestSimulation(unittest.TestCase):
    def test_run_episode_is_seed_deterministic_for_stable_fields(self) -> None:
        result1 = run_episode(
            strategy=GreedyStrategy(),
            rows=8,
            cols=8,
            max_steps=500,
            seed=42,
        )
        result2 = run_episode(
            strategy=GreedyStrategy(),
            rows=8,
            cols=8,
            max_steps=500,
            seed=42,
        )

        self.assertEqual(_stable_fields(result1), _stable_fields(result2))

    def test_run_batch_is_seed_deterministic_for_stable_fields(self) -> None:
        results1 = run_batch(
            strategy_factory=GreedyStrategy,
            episodes=5,
            rows=8,
            cols=8,
            max_steps=500,
            seed=99,
        )
        results2 = run_batch(
            strategy_factory=GreedyStrategy,
            episodes=5,
            rows=8,
            cols=8,
            max_steps=500,
            seed=99,
        )

        stable1 = [_stable_fields(result) for result in results1]
        stable2 = [_stable_fields(result) for result in results2]
        self.assertEqual(stable1, stable2)

# --- BFS Testing

    def test_bfs_episode_deterministic(self) -> None:
        result1 = run_episode(BreadthFirstStrategy(), 8, 8, 500, seed=42)
        result2 = run_episode(BreadthFirstStrategy(), 8, 8, 500, seed=42)

        self.assertEqual(_stable_fields(result1), _stable_fields(result2))

    def test_bfs_batch_deterministic(self) -> None:
        results1 = run_batch(BreadthFirstStrategy, 5, 8, 8, 500, seed=99)
        results2 = run_batch(BreadthFirstStrategy, 5, 8, 8, 500, seed=99)

        stable1 = [_stable_fields(r) for r in results1]
        stable2 = [_stable_fields(r) for r in results2]

        self.assertEqual(stable1, stable2)

# --- DFS Testing

    def test_dfs_episode_deterministic(self) -> None:
        result1 = run_episode(DepthFirstStrategy(), 8, 8, 500, seed=42)
        result2 = run_episode(DepthFirstStrategy(), 8, 8, 500, seed=42)

        self.assertEqual(_stable_fields(result1), _stable_fields(result2))

    def test_dfs_batch_deterministic(self) -> None:
        results1 = run_batch(DepthFirstStrategy, 5, 8, 8, 500, seed=99)
        results2 = run_batch(DepthFirstStrategy, 5, 8, 8, 500, seed=99)

        stable1 = [_stable_fields(r) for r in results1]
        stable2 = [_stable_fields(r) for r in results2]

        self.assertEqual(stable1, stable2)

# --- Hamiltonian Testing

    def test_hamiltonian_episiode_deterministic(self) -> None:
        result1 = run_episode(HamiltonianStrategy(), 6, 6, 500, seed=42)
        result2 = run_episode(HamiltonianStrategy(), 6, 6, 500, seed=42)

        self.assertEqual(_stable_fields(result1), _stable_fields(result2))
    
    def test_hamiltonian_batch_deterministic(self) -> None:
        results1 = run_batch(HamiltonianStrategy, 5, 6, 6, 500, seed=99)
        results2 = run_batch(HamiltonianStrategy, 5, 6, 6, 500, seed=99)

        stable1 = [_stable_fields(r) for r in results1]
        stable2 = [_stable_fields(r) for r in results2]

        self.assertEqual(stable1, stable2)

    def test_hamiltonian_odd_grid_raises(self) -> None:
        with self.assertRaises(ValueError):
            run_episode(HamiltonianStrategy(), 5, 5, 100, seed=1)

# --- ASTAR Testing

    def test_astar_episode_deterministic(self) -> None:
        result1 = run_episode(AStarStrategy(), 8, 8, 500, seed=42)
        result2 = run_episode(AStarStrategy(), 8, 8, 500, seed=42)

        self.assertEqual(_stable_fields(result1), _stable_fields(result2))

    def test_astar_batch_deterministic(self) -> None:
        results1 = run_batch(AStarStrategy, 5, 8, 8, 500, seed=99)
        results2 = run_batch(AStarStrategy, 5, 8, 8, 500, seed=99)

        stable1 = [_stable_fields(r) for r in results1]
        stable2 = [_stable_fields(r) for r in results2]

        self.assertEqual(stable1, stable2)


    def test_format_batch_summary_contains_core_metrics(self) -> None:
        results = [
            SimulationResult(steps=10, apples_eaten=2, won=False, game_over=True, max_steps_reached=False, elapsed_ms=1.0),
            SimulationResult(steps=20, apples_eaten=4, won=True, game_over=False, max_steps_reached=False, elapsed_ms=2.0),
        ]

        summary = format_batch_summary(results)

        self.assertIn("Episodes: 2", summary)
        self.assertIn("Wins: 1", summary)
        self.assertIn("Game overs: 1", summary)
        self.assertIn("Average apples eaten:", summary)


if __name__ == "__main__":
    unittest.main()
