"""
Snake movement strategies: given GameState, return (delta_row, delta_col).
May use algors (pathfinding, distances) but contain no core path math themselves.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from algors import *
from game_state import GameState


class SnakeStrategy(ABC):
    """Base class for movement strategies. State has .snake, .goal, .rows, .cols."""

    @abstractmethod
    def get_next_direction(self, state: GameState) -> tuple[int, int]:
        """Return (delta_row, delta_col) for the next move."""
        ...


class HamiltonianStrategy(SnakeStrategy):
    """Follow a Hamiltonian cycle so the snake eventually visits every cell. Path is computed once on first call."""

    '''
    Good
    6x6
    5x6
    '''
    def __init__(self) -> None:
        self._path: list[tuple[int, int]] | None = None
        # Cache from cell -> index in Hamiltonian cycle for fast lookups
        self._index_by_cell: dict[tuple[int, int], int] | None = None

    def _ensure_path(self, state: GameState) -> None:
        if self._path is None:
            head_row = state.snake[0][0]
            head_col = state.snake[0][1]
            self._path = hamiltonian_cycle(state.rows, state.cols, head_row, head_col)
            self._index_by_cell = {cell: i for i, cell in enumerate(self._path)}

    def _find_indices(
        self, state: GameState
    ) -> tuple[int | None, int | None, int | None]:
        """
        Return (head_idx, tail_idx, goal_idx) on the Hamiltonian cycle, or None if not found.
        """
        assert self._path is not None and self._index_by_cell is not None
        head = (state.snake[0][0], state.snake[0][1])
        tail = (state.snake[-1][0], state.snake[-1][1])
        goal = state.goal
        head_idx = self._index_by_cell.get(head)
        tail_idx = self._index_by_cell.get(tail)
        goal_idx = self._index_by_cell.get(goal) if goal is not None else None
        return head_idx, tail_idx, goal_idx

    def get_next_direction(self, state: GameState) -> tuple[int, int]:
        head_row = state.snake[0][0]
        head_col = state.snake[0][1]

        self._ensure_path(state)
        assert self._path is not None and self._index_by_cell is not None

        head = (head_row, head_col)
        head_idx = self._index_by_cell.get(head)
        if head_idx is None:
            # If somehow the head is not on the cycle, just keep the current direction.
            return state.direction

        if not self._path:
            return state.direction

        next_i = (head_idx + 1) % len(self._path)
        next_row, next_col = self._path[next_i]
        return next_row - head_row, next_col - head_col


class HamiltonianAStarStrategy(HamiltonianStrategy):
    """
    Hybrid strategy:
    - Mode A: follow Hamiltonian cycle by default (always-safe baseline).
    - Mode B: occasionally take A* shortcuts toward food when they are clearly safe.
    - Mode C: when the board is crowded / risky, disable shortcuts and stick to the cycle.
    """

    def __init__(self) -> None:
        super().__init__()

    # ---------- small helpers ----------

    @staticmethod
    def _ring_distance(a: int, b: int, n: int) -> int:
        """Forward distance from index a to b on a ring of size n."""
        return (b - a) % n

    @staticmethod
    def _is_between(a: int, b: int, x: int, n: int) -> bool:
        """Return True iff x is on the forward arc from a to b (inclusive of b)."""
        return (x - a) % n <= (b - a) % n

    @staticmethod
    def _neighbors(
        r: int, c: int, rows: int, cols: int
    ) -> list[tuple[int, int]]:
        res: list[tuple[int, int]] = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                res.append((nr, nc))
        return res

    def _astar_to_food(
        self,
        state: GameState,
        blocked: set[tuple[int, int]],
    ) -> list[tuple[int, int]] | None:
        """
        Grid-based A* from current head to food, treating `blocked` cells as obstacles.
        Returns path [start, ..., goal] or None.
        """
        if state.goal is None:
            return None

        start = (state.snake[0][0], state.snake[0][1])
        goal = state.goal
        rows, cols = state.rows, state.cols

        open_heap: list[tuple[float, int, tuple[int, int]]] = []
        g: dict[tuple[int, int], float] = {start: 0.0}
        parents: dict[tuple[int, int], tuple[int, int] | None] = {start: None}

        def h(cell: tuple[int, int]) -> float:
            return manhattan_distance(cell[0], cell[1], goal[0], goal[1])

        import heapq

        heapq.heappush(open_heap, (h(start), 0, start))
        visited: set[tuple[int, int]] = set()

        while open_heap:
            f, _, cell = heapq.heappop(open_heap)
            if cell in visited:
                continue
            visited.add(cell)
            if cell == goal:
                # Reconstruct path
                path: list[tuple[int, int]] = []
                cur: tuple[int, int] | None = cell
                while cur is not None:
                    path.append(cur)
                    cur = parents[cur]
                path.reverse()
                return path

            for nbr in self._neighbors(cell[0], cell[1], rows, cols):
                if nbr in blocked:
                    continue
                tentative_g = g[cell] + 1
                if tentative_g < g.get(nbr, float("inf")):
                    g[nbr] = tentative_g
                    parents[nbr] = cell
                    heapq.heappush(open_heap, (tentative_g + h(nbr), len(parents), nbr))

        return None

    # ---------- core decision logic ----------

    def get_next_direction(self, state: GameState) -> tuple[int, int]:
        """
        Each turn:
        1. Determine Hamiltonian baseline move.
        2. Optionally compute an A* shortcut toward food.
        3. Take the shortcut only if it is clearly safe; otherwise stick to the cycle.
        """
        # Ensure Hamiltonian cycle exists and indices are ready.
        self._ensure_path(state)
        assert self._path is not None and self._index_by_cell is not None

        n = len(self._path)
        head_row, head_col = state.snake[0][0], state.snake[0][1]
        head = (head_row, head_col)

        head_idx, tail_idx, goal_idx = self._find_indices(state)

        # Fallback: if we can't locate the head on the cycle, keep current direction.
        if head_idx is None:
            return state.direction

        # 1. Baseline move: follow Hamiltonian cycle (Mode A: safe cruise).
        baseline_next_idx = (head_idx + 1) % n
        baseline_next_row, baseline_next_col = self._path[baseline_next_idx]
        baseline_move = (
            baseline_next_row - head_row,
            baseline_next_col - head_col,
        )

        # If there is no food, just follow the cycle.
        if state.goal is None or goal_idx is None or tail_idx is None:
            return baseline_move

        # --- 2. Decide whether we should even consider a shortcut ---
        total_cells = state.rows * state.cols
        length = len(state.snake)
        free_cells = total_cells - length

        # Risk heuristics (Mode C: safety recovery)
        # More conservative when snake is long or board is crowded.
        crowded = length / total_cells > 0.6
        very_crowded = length / total_cells > 0.8 or free_cells < total_cells * 0.2

        if very_crowded:
            # Board too tight: force pure cycle-following.
            return baseline_move

        # Distance along the Hamiltonian cycle from head to food.
        cycle_distance_to_food = self._ring_distance(head_idx, goal_idx, n)

        # Only consider shortcuts if food is meaningfully ahead on the cycle.
        # If it is "behind" (i.e., requires almost a full loop), just keep cycling.
        if cycle_distance_to_food > n // 2:
            return baseline_move

        # If snake is moderately crowded, demand that the food is relatively close.
        if crowded and cycle_distance_to_food > n // 4:
            return baseline_move

        # --- 3. Try to find a shortcut using A* ---
        # Treat all body segments except the current head as blocked.
        blocked: set[tuple[int, int]] = {
            (r, c) for r, c in state.snake[1:]
        }

        path_to_food = self._astar_to_food(state, blocked)
        if not path_to_food or len(path_to_food) < 2:
            # No path or trivial: stay on cycle.
            return baseline_move

        # A* step count (excluding the start).
        astar_steps_to_food = len(path_to_food) - 1

        # Taking a shortcut must actually improve time to food.
        if astar_steps_to_food >= cycle_distance_to_food:
            return baseline_move

        # Compute the immediate A* move candidate.
        shortcut_target = path_to_food[1]
        shortcut_idx = self._index_by_cell.get(shortcut_target)

        if shortcut_idx is None:
            # Should not happen because the Hamiltonian cycle covers all cells,
            # but if it does, be conservative and reject the shortcut.
            return baseline_move

        # --- Safety checks on the shortcut (Mode B: safe food collection) ---

        # 1. It must not jump into or beyond the body segment currently occupied.
        # Require that the new head index lies between head and tail along the cycle.
        # This preserves the ordering of the body along the cycle.
        if not self._is_between(head_idx, tail_idx, shortcut_idx, n):
            return baseline_move

        # 2. Do not skip too many cycle positions in a single jump.
        skipped = self._ring_distance(head_idx, shortcut_idx, n) - 1
        max_skip = max(3, free_cells // 4)
        if skipped > max_skip:
            return baseline_move

        # 3. If the benefit is only marginal, avoid the risk and stick to the cycle.
        gain = cycle_distance_to_food - astar_steps_to_food
        min_gain = 2 if not crowded else 3
        if gain < min_gain:
            return baseline_move

        # At this point the shortcut is considered "clearly safe enough":
        # - It improves arrival time.
        # - It keeps the snake ordered along the cycle.
        # - It does not collide now or jump into the occupied cycle segment.
        # -> Take the shortcut move.
        next_row, next_col = shortcut_target
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


class BreadthFirstStrategy(SnakeStrategy):

    def get_next_direction(self, state: GameState) -> tuple[int, int]:
        if len(state.path) == 0:
            grid = Grid(state.rows, state.cols)
            problem = SnakeProblem(initial=state.snake[0],goal=state.goal,grid=grid)
            path = path_states(breadth_first_bfs(problem))
            path.pop(0)
            state.path= path

        head_row, head_col = state.snake[0][0], state.snake[0][1]
        next_row, next_col = state.path.pop(0)

        return next_row - head_row, next_col - head_col
    

class DepthFirstStrategy(SnakeStrategy):

    def get_next_direction(self, state: GameState) -> tuple[int, int]:
        if len(state.path) == 0:
            grid = Grid(state.rows, state.cols)
            problem = SnakeProblem(initial=state.snake[0],goal=state.goal,grid=grid)
            path = path_states(depth_first_bfs(problem))
            path.pop(0)
            state.path= path

        head_row, head_col = state.snake[0][0], state.snake[0][1]
        next_row, next_col = state.path.pop(0)

        return next_row - head_row, next_col - head_col



class AStarStrategy(SnakeStrategy):

    def get_next_direction(self, state: GameState) -> tuple[int, int]:
        if len(state.path) == 0:
            grid = Grid(state.rows, state.cols)
            problem = SnakeProblem(initial=state.snake[0],goal=state.goal,grid=grid)
            path = path_states(astar_search(problem))
            path.pop(0)
            state.path= path

        head_row, head_col = state.snake[0][0], state.snake[0][1]
        next_row, next_col = state.path.pop(0)

        return next_row - head_row, next_col - head_col

