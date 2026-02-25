"""
Snake game: SnakeGame is the application (window + grid + input). GameState lives in game_state.py.
"""
from __future__ import annotations

import os
import tkinter as tk
from PIL import Image, ImageTk

from game_state import GameState
from strategies import SnakeStrategy

# -----------------------------------------------------------------------------
# Constants (drawing only; grid size and speed come from SnakeGame args)
# -----------------------------------------------------------------------------

CELL_SIZE = 60
OVERLAY_MARGIN = 40
OVERLAY_FONT_TITLE = ("Arial", 24, "bold")
OVERLAY_FONT_SUBTITLE = ("Arial", 12)


# -----------------------------------------------------------------------------
# SnakeGame: main application. Owns the grid (canvas), state, and input.
# -----------------------------------------------------------------------------


class SnakeGame(tk.Tk):
    """Snake game application. Contains the grid (canvas), draws the state, and handles input/tick."""

    def __init__(
        self,
        rows: int = 6,
        cols: int = 6,
        tick_ms: int = 100,
        strategy: SnakeStrategy | None = None,
    ):
        super().__init__()
        self.title("Snake Game")
        self.resizable(False, False)

        self._rows = rows
        self._cols = cols
        self._tick_ms = tick_ms
        self.state = GameState(rows=rows, cols=cols)
        self._strategy = strategy  # None = play with arrow keys
        self._tick_job: str | None = None

        self._build_canvas()
        self._draw_grid()
        self._load_head_images()
        self._draw_goal()
        self._draw_snake()
        self.bind("<Escape>", self._on_escape)

        if self._strategy is None:
            self._bind_keys()
        else:
            self._schedule_tick()

    # --- Main flow ---

    def _schedule_tick(self) -> None:
        if self._tick_job is None:
            self._tick_job = self.after(self._tick_ms, self._tick)

    def _tick(self) -> None:
        self._tick_job = None
        if self.state.state_over or self.state.state_won:
            return
        delta_row, delta_col = self._strategy.get_next_direction(self.state)
        self._move(delta_row, delta_col)
        self._schedule_tick()

    def _move(self, delta_row: int, delta_col: int) -> None:
        """Apply one move. Caller must pass the direction (from key or from strategy)."""
        if self.state.state_over or self.state.state_won:
            return
        if self._strategy is None:
            if len(self.state.snake) > 1:
                current_delta_row, current_delta_col = self.state.direction
                if (delta_row, delta_col) == (-current_delta_row, -current_delta_col):
                    return
            head_row, head_col = self.state.snake[0]
            next_row = head_row + delta_row
            next_col = head_col + delta_col
            if not (0 <= next_row < self.state.rows and 0 <= next_col < self.state.cols):
                return

        if not self.state.step(delta_row, delta_col):
            if self.state.state_over:
                self._draw_snake()
                self._draw_overlay(
                    "game_over", "black", "white",
                    "Game Over", "Press Esc to reset.",
                    "white", "lightgray",
                )
                if self._strategy is None:
                    self._unbind_keys()
            return

        self._draw_goal()
        self._draw_snake()
        if self.state.state_won:
            self._draw_overlay(
                "game_win", "darkgreen", "gold",
                "You Win!", "Board complete!",
                "gold", "lightgreen",
            )
            if self._strategy is None:
                self._unbind_keys()

    # --- Input ---

    def _bind_keys(self) -> None:
        """Arrow keys call _move with the corresponding direction. Only used when strategy is None."""
        self.bind("<Up>", lambda e: self._move(-1, 0))
        self.bind("<Down>", lambda e: self._move(1, 0))
        self.bind("<Left>", lambda e: self._move(0, -1))
        self.bind("<Right>", lambda e: self._move(0, 1))

    def _unbind_keys(self) -> None:
        self.unbind("<Up>")
        self.unbind("<Down>")
        self.unbind("<Left>")
        self.unbind("<Right>")

    def _on_escape(self, _event: tk.Event) -> None:
        if self.state.state_over:
            self._reset_game()

    def _reset_game(self) -> None:
        if self._tick_job is not None:
            self.after_cancel(self._tick_job)
            self._tick_job = None
        self.canvas.delete("game_over")
        self.canvas.delete("game_win")
        self.state = GameState(rows=self._rows, cols=self._cols)
        self._draw_goal()
        self._draw_snake()
        if self._strategy is None:
            self._bind_keys()
        else:
            self._schedule_tick()

    # --- Drawing ---

    def _draw_snake(self) -> None:
        self.canvas.delete("player")
        for i, (row, col) in enumerate(self.state.snake):
            x1, y1, x2, y2 = self._cell_to_xy(row, col)
            if i == 0:
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                img = self._head_images.get(self.state.direction, self._head_images[(1, 0)])
                self.canvas.create_image(cx, cy, image=img, tags="player")
            else:
                self.canvas.create_oval(x1, y1, x2, y2, fill="blue", tags="player")

    def _draw_goal(self) -> None:
        self.canvas.delete("goal")
        if self.state.goal is None:
            return
        r, c = self.state.goal
        x1 = c * CELL_SIZE + 15
        y1 = r * CELL_SIZE + 15
        x2 = x1 + CELL_SIZE - 30
        y2 = y1 + CELL_SIZE - 30
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="red", tags="goal")

    def _draw_overlay(self, tag: str, bg: str, outline: str, title: str, subtitle: str, title_fill: str, subtitle_fill: str) -> None:
        w = self._cols * CELL_SIZE
        h = self._rows * CELL_SIZE
        m = OVERLAY_MARGIN
        self.canvas.create_rectangle(m, m, w - m, h - m, fill=bg, outline=outline, width=3, tags=tag)
        self.canvas.create_text(w // 2, h // 2, text=title, fill=title_fill, font=OVERLAY_FONT_TITLE, tags=tag)
        self.canvas.create_text(w // 2, h // 2 + 32, text=subtitle, fill=subtitle_fill, font=OVERLAY_FONT_SUBTITLE, tags=tag)

    # --- Setup helpers ---

    def _build_canvas(self) -> None:
        self.canvas = tk.Canvas(
            self,
            width=self._cols * CELL_SIZE,
            height=self._rows * CELL_SIZE,
            bg="green",
        )
        self.canvas.pack()

    def _draw_grid(self) -> None:
        for r in range(self._rows):
            for c in range(self._cols):
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black")

    def _load_head_images(self) -> None:
        """Load snake head image and create 4 rotated copies (one per direction)."""
        head_size = CELL_SIZE - 12
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snake.png")
        pil_img = Image.open(path).resize((head_size, head_size), Image.LANCZOS)
        angles = {(1, 0): 0, (-1, 0): 180, (0, 1): 90, (0, -1): -90}
        self._head_images = {}
        for (dr, dc), angle in angles.items():
            rotated = pil_img.rotate(angle, expand=False)
            self._head_images[(dr, dc)] = ImageTk.PhotoImage(rotated)

    def _cell_to_xy(self, row: int, col: int) -> tuple[float, float, float, float]:
        """Return (x1, y1, x2, y2) for the body segment rectangle in a cell."""
        x1 = col * CELL_SIZE + 10
        y1 = row * CELL_SIZE + 10
        x2 = x1 + CELL_SIZE - 20
        y2 = y1 + CELL_SIZE - 20
        return x1, y1, x2, y2
