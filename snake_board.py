from __future__ import annotations

import os
import random
import time
import tkinter as tk
from PIL import Image, ImageTk

from game_state import GameState
from strategies import SnakeStrategy


CELL_SIZE = 70
OVERLAY_MARGIN = 40
ROWS = 5
COLS = 6
OVERLAY_FONT_TITLE = ("Arial", 24, "bold")
OVERLAY_FONT_SUBTITLE = ("Arial", 12)


class SnakeGame(tk.Tk):

    def __init__(
        self,
        rows = ROWS,
        cols = COLS,
        tick_ms: int = 100,
        strategy: SnakeStrategy | None = None,
        seed: int | None = None,
    ):
        super().__init__()

        self.title("Snake Game")
        board_w = cols * CELL_SIZE
        board_h = rows * CELL_SIZE

        self.geometry(f"{board_w + 260}x{board_h + 20}")
        self.resizable(True, True)

        self._rows = rows
        self._cols = cols
        self._tick_ms = tick_ms
        self._seed = seed

        self._build_layout()
        self._build_canvas()
        self._build_metrics()

        self.state = self._new_state()

        self._strategy = strategy
        self._tick_job = None

        self._moves = 0
        self._apples_eaten = 0
        self._total_reward = 0

        self._run_started_at = time.perf_counter()
        self._metrics_reported = False

        self._draw_grid()
        self._load_head_images()
        self._draw_goal()
        self._draw_snake()

        self.bind("<Escape>", self._on_escape)

        if self._strategy is None:
            self._bind_keys()
            self._mode_var.set("Mode: manual")
        else:
            self._schedule_tick()
            self._mode_var.set("Mode: strategy")

        self._update_metrics()

    # ------------------------------------------------------------
    # State
    # ------------------------------------------------------------

    def _new_state(self):
        rng = random.Random(self._seed)
        return GameState(rows=self._rows, cols=self._cols, rng=rng)

    # ------------------------------------------------------------
    # Game Loop
    # ------------------------------------------------------------

    def _schedule_tick(self):
        if self._tick_job is None:
            self._tick_job = self.after(self._tick_ms, self._tick)

    def _tick(self):
        self._tick_job = None

        if self.state.state_over or self.state.state_won:
            return

        delta_row, delta_col = self._strategy.get_next_direction(self.state)

        self._move(delta_row, delta_col)

        self._schedule_tick()

    # ------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------

    def _move(self, delta_row, delta_col):

        if self.state.state_over or self.state.state_won:
            return

        if self._strategy is None:

            if len(self.state.snake) > 1:
                dr, dc = self.state.direction
                if (delta_row, delta_col) == (-dr, -dc):
                    return

        head_row, head_col = self.state.snake[0]
        next_row = head_row + delta_row
        next_col = head_col + delta_col

        reward = self._calculate_reward(next_row, next_col)
        self._total_reward += reward

        if not self.state.step(delta_row, delta_col):

            if self.state.state_over:

                self._draw_snake()

                self._draw_overlay(
                    "game_over",
                    "black",
                    "white",
                    "Game Over",
                    "Press Esc to reset.",
                    "white",
                    "lightgray",
                )

                self._report_metrics("loss")

                if self._strategy is None:
                    self._unbind_keys()

            return

        self._moves += 1
        self._apples_eaten = len(self.state.snake) - 1

        self._draw_goal()
        self._draw_snake()

        if self.state.state_won:

            self._draw_overlay(
                "game_win",
                "darkgreen",
                "gold",
                "You Win!",
                "Board complete!",
                "gold",
                "lightgreen",
            )

            self._report_metrics("win")

            if self._strategy is None:
                self._unbind_keys()

    # ------------------------------------------------------------
    # Reward
    # ------------------------------------------------------------

    def _calculate_reward(self, next_row, next_col):

        goal = self.state.goal

        if goal and (next_row, next_col) == goal:
            return 1000

        if goal:
            dist = abs(goal[0] - next_row) + abs(goal[1] - next_col)
            if dist == 1:
                return -0.5

        return -1

    # ------------------------------------------------------------
    # Metrics (NEW CENTRAL SYSTEM)
    # ------------------------------------------------------------

    def _update_metrics(self):

        if not (self.state.state_over or self.state.state_won):

            elapsed = time.perf_counter() - self._run_started_at
            self._runtime_var.set(f"Runtime (s): {elapsed:.2f}")

            self.after(100, self._update_metrics)

        coverage = len(self.state.snake) / (self._rows * self._cols) * 100

        self._moves_var.set(f"Moves: {self._moves}")
        self._apples_var.set(f"Apples eaten: {self._apples_eaten}")
        self._length_var.set(f"Final length: {len(self.state.snake)} / {self._rows * self._cols}")
        self._coverage_var.set(f"Board coverage: {coverage:.1f}%")
        self._reward_var.set(f"Total reward: {self._total_reward:.1f}")

        if self._strategy is None:
            self._strategy_var.set("Strategy: None")
        else:
            self._strategy_var.set(f"Strategy: {self._strategy.__class__.__name__}")

    # ------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------

    def _reset_game(self):

        if self._tick_job:
            self.after_cancel(self._tick_job)

        self.canvas.delete("game_over")
        self.canvas.delete("game_win")

        self.state = self._new_state()

        self._moves = 0
        self._apples_eaten = 0
        self._total_reward = 0

        self._run_started_at = time.perf_counter()

        self._draw_goal()
        self._draw_snake()

        if self._strategy is None:
            self._bind_keys()
        else:
            self._schedule_tick()

        self._update_metrics()

    # ------------------------------------------------------------
    # Input
    # ------------------------------------------------------------

    def _bind_keys(self):

        self.bind("<Up>", lambda e: self._move(-1, 0))
        self.bind("<Down>", lambda e: self._move(1, 0))
        self.bind("<Left>", lambda e: self._move(0, -1))
        self.bind("<Right>", lambda e: self._move(0, 1))

    def _unbind_keys(self):

        self.unbind("<Up>")
        self.unbind("<Down>")
        self.unbind("<Left>")
        self.unbind("<Right>")

    def _on_escape(self, event):

        if self.state.state_over:
            self._reset_game()

    # ------------------------------------------------------------
    # Reporting Metrics
    # ------------------------------------------------------------

    def _report_metrics(self, outcome):

        if self._metrics_reported:
            return

        self._metrics_reported = True

        coverage = len(self.state.snake) / (self._rows * self._cols) * 100
        runtime = time.perf_counter() - self._run_started_at

        print("\n--- Visual Run Metrics ---")
        print("Outcome:", outcome)
        print("Moves:", self._moves)
        print("Apples:", self._apples_eaten)
        print("Coverage:", f"{coverage:.1f}%")
        print("Runtime:", f"{runtime:.2f}s")

    # ------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------

    def _draw_overlay(
    self,
    tag,
    bg,
    outline,
    title,
    subtitle,
    title_fill,
    subtitle_fill
):
        """Draw win/lose overlay."""

        w = self._cols * CELL_SIZE
        h = self._rows * CELL_SIZE
        m = OVERLAY_MARGIN

        self.canvas.create_rectangle(
            m, m, w - m, h - m,
            fill=bg,
            outline=outline,
            width=3,
            tags=tag
        )

        self.canvas.create_text(
            w // 2,
            h // 2,
            text=title,
            fill=title_fill,
            font=OVERLAY_FONT_TITLE,
            tags=tag
        )

        self.canvas.create_text(
            w // 2,
            h // 2 + 32,
            text=subtitle,
            fill=subtitle_fill,
            font=OVERLAY_FONT_SUBTITLE,
            tags=tag
        )


    def _draw_grid(self):
        for r in range(self._rows):
            for c in range(self._cols):
                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    outline="black"
                )

    def _draw_snake(self):

        self.canvas.delete("player")

        for i, (r, c) in enumerate(self.state.snake):

            x1, y1, x2, y2 = self._cell_to_xy(r, c)

            if i == 0:

                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2

                img = self._head_images.get(
                    self.state.direction, self._head_images[(1, 0)]
                )

                self.canvas.create_image(cx, cy, image=img, tags="player")

            else:

                self.canvas.create_oval(x1, y1, x2, y2, fill="blue", tags="player")

    def _draw_goal(self):

        self.canvas.delete("goal")

        if self.state.goal is None:
            return

        r, c = self.state.goal

        x1 = c * CELL_SIZE + 15
        y1 = r * CELL_SIZE + 15
        x2 = x1 + CELL_SIZE - 30
        y2 = y1 + CELL_SIZE - 30

        self.canvas.create_rectangle(x1, y1, x2, y2, fill="red", tags="goal")

    # ------------------------------------------------------------
    # Setup UI 
    # ------------------------------------------------------------

    def _build_layout(self):

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.board_frame = tk.Frame(self)
        self.board_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.metrics_frame = tk.Frame(self, bd=2, relief="ridge", width=220)
        self.metrics_frame.grid(row=0, column=1, sticky="ns", padx=10, pady=10)

    def _build_canvas(self):

        self.canvas = tk.Canvas(
            self.board_frame,
            width=self._cols * CELL_SIZE,
            height=self._rows * CELL_SIZE,
            bg="green",
            highlightthickness=0,
        )

        self.canvas.pack(expand=True, fill="both")

    def _build_metrics(self):

        tk.Label(
            self.metrics_frame,
            text="Run Metrics",
            font=("Arial", 14, "bold"),
        ).pack(pady=10)

        self._mode_var = tk.StringVar(value="Mode: manual")
        self._outcome_var = tk.StringVar(value="Outcome: running")
        self._moves_var = tk.StringVar(value="Moves: 0")
        self._apples_var = tk.StringVar(value="Apples eaten: 0")
        self._length_var = tk.StringVar()
        self._coverage_var = tk.StringVar()
        self._strategy_var = tk.StringVar(value="Strategy: None")
        self._runtime_var = tk.StringVar(value="Runtime (s): 0.00")
        self._avg_runtime_var = tk.StringVar()
        self._reward_var = tk.StringVar(value="Total reward: 0")

        vars = [
            self._mode_var,
            self._outcome_var,
            self._moves_var,
            self._apples_var,
            self._length_var,
            self._coverage_var,
            self._strategy_var,
            self._runtime_var,
            self._avg_runtime_var,
            self._reward_var,
        ]

        for v in vars:

            tk.Label(
                self.metrics_frame,
                textvariable=v,
                font=("Arial", 11),
                anchor="w",
            ).pack(fill="x", padx=10, pady=2)

    # ------------------------------------------------------------

    def _load_head_images(self):

        head_size = CELL_SIZE - 12

        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "snake.png",
        )

        pil_img = Image.open(path).resize((head_size, head_size))

        angles = {(1, 0): 0, (-1, 0): 180, (0, 1): 90, (0, -1): -90}

        self._head_images = {}

        for d, a in angles.items():

            rotated = pil_img.rotate(a)

            self._head_images[d] = ImageTk.PhotoImage(rotated)

    def _cell_to_xy(self, row, col):

        x1 = col * CELL_SIZE + 10
        y1 = row * CELL_SIZE + 10
        x2 = x1 + CELL_SIZE - 20
        y2 = y1 + CELL_SIZE - 20

        return x1, y1, x2, y2