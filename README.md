# snake-801

Snake game project for class 801: Foundations of AI. Play manually with arrow keys or run automated strategies (e.g. Hamiltonian cycle, greedy).

## Run the game

```bash
pip install -r requirements.txt
python main.py
```

Edit `main.py` to choose manual play (`strategy=None`) or a strategy (e.g. `HamiltonianStrategy()`), and optionally set `rows`, `cols`, `tick_ms`.

## File structure

| File | Role |
|------|------|
| **main.py** | Entry point. Creates the game and runs the UI loop. |
| **game_state.py** | Domain: `GameState` — snake position, goal, rules (step, spawn_goal). No UI. |
| **snake_board.py** | UI: `SnakeGame` — tkinter window, canvas, drawing, key input, tick loop. |
| **strategies.py** | Movement strategies: given `GameState`, return next direction `(delta_row, delta_col)`. |
| **algors.py** | Pure grid algorithms: distances (e.g. Manhattan), paths (e.g. Hamiltonian cycle). No game concepts. |

- **main** → **snake_board** (and strategies) → **game_state**
- **strategies** → **game_state**, **algors**
- **snake_board** does not import **strategies** except in `main.py` when building the game.

## Configuration

`SnakeGame` and `GameState` accept optional parameters with defaults:

- **rows** (default `6`) — grid row count
- **cols** (default `6`) — grid column count  
- **tick_ms** (default `100`) — milliseconds between each move (lower = faster)
- **strategy** (default `None`) — `None` for manual (arrow keys), or a strategy instance for auto play

Example:

```python
from snake_board import SnakeGame
from strategies import HamiltonianStrategy, GreedyStrategy

# Manual, 6×6, 100 ms tick
game = SnakeGame()

# Hamiltonian strategy, 8×8 grid, slower tick
game = SnakeGame(rows=8, cols=8, tick_ms=150, strategy=HamiltonianStrategy())
game.mainloop()
```

## Strategies

- **Manual** — `strategy=None`. Arrow keys call `_move` with the corresponding direction.
- **HamiltonianStrategy()** — follows a Hamiltonian cycle; path is computed once on first move. Fills the board without hitting itself.
- **GreedyStrategy()** — each step moves toward the goal by Manhattan distance. Can trap itself.

To add a new strategy: subclass `SnakeStrategy` in `strategies.py`, implement `get_next_direction(self, state: GameState) -> tuple[int, int]`, and pass an instance into `SnakeGame(strategy=...)`. No constructor arguments are required; state is passed each tick.

## Game rules

- **Lose** — snake hits the wall or its own body. Game over overlay is shown and input is disabled.
- **Win** — snake fills the entire grid (length = rows × cols). Win overlay is shown.

## Dependencies

- Python 3.9+
- **Pillow** — for resizing and rotating the snake head image (see `requirements.txt`)
- **tkinter** — usually bundled with Python
