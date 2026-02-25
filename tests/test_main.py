import argparse
import unittest
from unittest import mock

import main
from strategies import GreedyStrategy, HamiltonianStrategy


class TestMain(unittest.TestCase):
    def test_parse_args_defaults(self) -> None:
        with mock.patch("sys.argv", ["main.py"]):
            args = main._parse_args()

        self.assertEqual(args.mode, "visual")
        self.assertEqual(args.strategy, "manual")
        self.assertEqual(args.rows, 8)
        self.assertEqual(args.cols, 8)
        self.assertEqual(args.tick_ms, 100)
        self.assertEqual(args.episodes, 1)
        self.assertEqual(args.max_steps, 1000)
        self.assertIsNone(args.seed)

    def test_build_strategy(self) -> None:
        self.assertIsNone(main._build_strategy("manual"))
        self.assertIsInstance(main._build_strategy("greedy"), GreedyStrategy)
        self.assertIsInstance(main._build_strategy("hamiltonian"), HamiltonianStrategy)

    def test_validate_args_rejects_manual_headless(self) -> None:
        args = argparse.Namespace(
            mode="headless",
            strategy="manual",
            rows=8,
            cols=8,
            tick_ms=100,
            episodes=1,
            max_steps=1000,
            seed=None,
        )

        with self.assertRaises(ValueError):
            main._validate_args(args)

    def test_validate_args_rejects_odd_hamiltonian_grid(self) -> None:
        args = argparse.Namespace(
            mode="visual",
            strategy="hamiltonian",
            rows=5,
            cols=5,
            tick_ms=100,
            episodes=1,
            max_steps=1000,
            seed=7,
        )

        with self.assertRaises(ValueError):
            main._validate_args(args)


if __name__ == "__main__":
    unittest.main()
