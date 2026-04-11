import unittest

from algors import hamiltonian_cycle, manhattan_distance, astar_search, depth_first_bfs, breadth_first_bfs, best_first_search
from algors import Grid, SnakeProblem, path_states


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

    def test_breadth_first_bfs(self):
        grid = Grid(8,8)
        problem = SnakeProblem(initial=(0,0), goal=(7,7), grid=grid)

        result = breadth_first_bfs(problem)
        path = path_states(result)

        self.assertEqual(path[-1], (7,7))

        self.assertEqual(len(path) - 1, 14)

    def test_astar_search(self):
        grid = Grid(8,8)
        problem = SnakeProblem(initial=(0,0), goal=(7,7), grid=grid)

        result = astar_search(problem)
        path = path_states(result)

        self.assertEqual(path[-1], (7,7))

        self.assertEqual(len(path) - 1, 14)

    def test_depth_first_bfs(self):

        grid = Grid(8, 8)
        problem = SnakeProblem(initial=(0, 0), goal=(7, 7), grid=grid)

        result = depth_first_bfs(problem)
        path = path_states(result)

        self.assertEqual(path[-1], (7, 7))  

        self.assertTrue(len(path) >= 14)
    
    def test_best_first_search(self):
        grid = Grid(8,8)
        problem = SnakeProblem(initial=(0,0), goal=(7,7), grid=grid)

        result = astar_search(problem)
        path = path_states(result)

        self.assertEqual(path[-1], (7,7))

        self.assertEqual(len(path) - 1, 14)

if __name__ == "__main__":
    unittest.main()
