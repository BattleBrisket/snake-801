import unittest

from algors import hamiltonian_cycle, manhattan_distance


class TestAlgors(unittest.TestCase):
    def test_manhattan_distance(self) -> None:
        self.assertEqual(manhattan_distance(0, 0, 3, 4), 7)
        self.assertEqual(manhattan_distance(2, 2, 2, 2), 0)

    def test_hamiltonian_cycle_even_grid_returns_valid_cycle(self) -> None:
        path = hamiltonian_cycle(4, 4, 0, 0)
        self.assertEqual(len(path), 16)
        self.assertEqual(len(set(path)), 16)
        self.assertEqual(path[0], (0, 0))

        for index in range(len(path)):
            row1, col1 = path[index]
            row2, col2 = path[(index + 1) % len(path)]
            self.assertEqual(abs(row1 - row2) + abs(col1 - col2), 1)

    def test_hamiltonian_cycle_odd_by_odd_raises(self) -> None:
        with self.assertRaises(ValueError):
            hamiltonian_cycle(5, 5, 0, 0)


if __name__ == "__main__":
    unittest.main()
