# BFS: Big Fancy Serpent

Snake game project for class 801: Foundations of AI.
Play manually with arrow keys or run automated strategies (e.g. Hamiltonian cycle, greedy).

## Run the game

```bash
pip install -r requirements.txt
```

Interactive (visual) mode examples:

```bash
# manual controls (arrow keys)
python3 main.py --mode visual --strategy manual

# automated play in the UI
python3 main.py --mode visual --strategy greedy

# automated play in the UI with reproducible randomness
python3 main.py --mode visual --strategy greedy --seed 42

# automated play with a custom grid layout and tick timing
python3 main.py --mode visual --strategy greedy --rows 8 --cols 8 --tick-ms 120
```

Headless mode example:

```bash
python3 main.py --mode headless --strategy greedy --episodes 100 --rows 8 --cols 8 --max-steps 2000 --seed 42
```

## File structure

| File | Role |
|------|------|
| **main.py** | Entry point. Creates the game and runs the UI loop. |
| **game_state.py** | Domain: `GameState` - snake position, goal, rules (step, spawn_goal). No UI. |
| **snake_board.py** | UI: `SnakeGame` - tkinter window, canvas, drawing, key input, tick loop. |
| **strategies.py** | Movement strategies: given `GameState`, return next direction `(delta_row, delta_col)`. |
| **algors.py** | Pure grid algorithms: distances (e.g. Manhattan), paths (e.g. Hamiltonian cycle). No game concepts. |
| **simulation.py** | Headless simulation runner for batch episodes + metrics output. |

- **main** → **snake_board** (and strategies) → **game_state**
- **main** → **simulation** (headless mode) → **game_state**, **strategies**
- **strategies** → **game_state**, **algors**

## Command line arguments

Use `python3 main.py --help` to print the full CLI help.

Common arguments (both modes):

| Argument | Default | Details |
|---|---|---|
| `--mode` | `visual` | `visual` (interactive UI) or `headless` (no UI simulation). |
| `--strategy` | `manual` | `manual`, `greedy`, `hamiltonian`. `manual` is valid only in `visual` mode. |
| `--rows` | `8` | Grid row count. Must be `> 0`. |
| `--cols` | `8` | Grid column count. Must be `> 0`. |
| `--seed` | unset | Random seed for reproducible snake spawn, first apple, and all subsequent apple placements. |

Interactive-only arguments:

| Argument | Default | Details |
|---|---|---|
| `--tick-ms` | `100` | Milliseconds between moves in UI. Smaller values run faster. |

Headless-only arguments:

| Argument | Default | Details |
|---|---|---|
| `--episodes` | `1` | Number of simulation episodes to run. Must be `> 0`. |
| `--max-steps` | `1000` | Per-episode step limit. Simulation stops early if this limit is hit. Must be `> 0`. |

## Strategies

- **Manual** - `--strategy manual` (visual mode only). Arrow keys call `_move` with the corresponding direction.
- **Hamiltonian** - `--strategy hamiltonian`; follows a Hamiltonian cycle computed on first move.
- **Greedy** - `--strategy greedy`; each step moves toward the goal by Manhattan distance and can trap itself.

To add a new strategy: subclass `SnakeStrategy` in `strategies.py`, implement `get_next_direction(self, state: GameState) -> tuple[int, int]`, then wire it into `_build_strategy` in `main.py`.

## Game rules

- **Lose** - snake hits the wall or its own body. Game over overlay is shown and input is disabled.
- **Win** - snake fills the entire grid (length = rows × cols). Win overlay is shown.

## Dependencies

- Python 3.9+
- **Pillow** - for resizing and rotating the snake head image (see `requirements.txt`)
- **tkinter** - usually bundled with Python

## Run unit tests

From the project root:

```bash
python3 -m unittest discover -s tests -v
```

Run a single test module:

```bash
python3 -m unittest -v tests.test_game_state
```

Run a single test class:

```bash
python3 -m unittest -v tests.test_simulation.TestSimulation
```
