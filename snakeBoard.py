import os
import tkinter as tk
import random
from collections import deque
from PIL import Image, ImageTk

# Grid settings
grid_size = 6
ROWS = grid_size
COLS = grid_size
CELL_SIZE = 60   # Pixel size of each grid square

# Speed: milliseconds between each move (lower = faster)
TICK_MS = 100

# Toggle
auto_run = True


class GameGrid(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window settings
        self.title("Snake Game")
        self.resizable(False, False)

        # Create canvas (game drawing area)
        self.canvas = tk.Canvas(
            self,
            width=COLS * CELL_SIZE,
            height=ROWS * CELL_SIZE,
            bg="green"
        )
        self.canvas.pack()

        # Draw the grid lines
        for r in range(ROWS):
            for c in range(COLS):
                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black")

        # Store player as list (row, column)
        self.player_list = [[2,2]]
        # Last movement direction (dr, dc); image default is down (1, 0)
        self.last_direction = (1, 0)

        # Head image in 4 rotations: original faces down, keyed by (dr, dc)
        head_size = CELL_SIZE - 12
        head_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snake.png")
        pil_img = Image.open(head_path).resize((head_size, head_size), Image.LANCZOS)
        # (dr, dc) -> rotation in degrees (original = down)
        direction_angles = {(1, 0): 0, (-1, 0): 180, (0, 1): 90, (0, -1): -90}
        self.head_images = {}
        for (dr, dc), angle in direction_angles.items():
            rotated = pil_img.rotate(angle, expand=False)
            self.head_images[(dr, dc)] = ImageTk.PhotoImage(rotated)

        # Goal state variables
        self.goal_row = None
        self.goal_col = None
        self.goal = None
        self.spawn_goal()  # Create first goal

        # Draw player on screen
        self.player = self.draw_player(self.player_list)

        # Bind arrow keys to player movement
        if auto_run == False:
            self.bind("<Up>", lambda e: self.move_player(-1, 0))
            self.bind("<Down>", lambda e: self.move_player(1, 0))
            self.bind("<Left>", lambda e: self.move_player(0, -1))
            self.bind("<Right>", lambda e: self.move_player(0, 1))
        else:
            from algors import hamiltonian_cycle
            self.path = deque(hamiltonian_cycle(ROWS,COLS,self.player_list[0][0],self.player_list[0][1]))

        # Controls whether update loop continues
        self.game_continue = False

        # Game over when snake hits itself
        self.game_over = False
        # Win when snake fills the board
        self.game_won = False

        # Start update loop
        self.update_loop()

    def draw_player(self, player_list):
        """Draw player: head (index 0) as image, body segments as blue circles."""
        canvas_drawn = []
        for i, coord in enumerate(player_list):
            x1 = coord[1] * CELL_SIZE + 10
            y1 = coord[0] * CELL_SIZE + 10
            x2 = x1 + CELL_SIZE - 20
            y2 = y1 + CELL_SIZE - 20
            if i == 0:
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                head_img = self.head_images.get(self.last_direction, self.head_images[(1, 0)])
                canvas_drawn.append(self.canvas.create_image(cx, cy, image=head_img, tags="player"))
            else:
                canvas_drawn.append(self.canvas.create_oval(x1, y1, x2, y2, fill="blue", tags="player"))
        return canvas_drawn

    def move_player(self, dr, dc):
        """Move player if inside grid boundaries."""

        if self.game_over or self.game_won:
            return

        if auto_run:
            # Cycle path
            last_point = self.path.popleft()
            self.path.append(last_point)
            new_point = self.path[0]
            dr = new_point[0] - self.player_list[0][0]
            dc = new_point[1] - self.player_list[0][1]

        # Stop movement if hitting window border
        if not (0 <= self.player_list[0][0]+dr < ROWS and 0 <= self.player_list[0][1]+dc < COLS):
            print("hit window barrier!")
            return

        new_head_row = self.player_list[0][0] + dr
        new_head_col = self.player_list[0][1] + dc

        # Game over if head hits body (any segment except current head)
        for i in range(1, len(self.player_list)):
            if self.player_list[i][0] == new_head_row and self.player_list[i][1] == new_head_col:
                self.game_over = True
                self.show_game_over()
                print("Game Over - snake hit its own body!")
                if not auto_run:
                    self.unbind("<Up>")
                    self.unbind("<Down>")
                    self.unbind("<Left>")
                    self.unbind("<Right>")
                return

        last_row = self.player_list[-1][0]
        last_col = self.player_list[-1][1]

        for i, _ in reversed(list(enumerate(self.player_list))):
            # Calculate new position
            if i == 0:
                self.player_list[i][0] += dr
                self.player_list[i][1] += dc
            else:
                self.player_list[i][0] = self.player_list[i-1][0]
                self.player_list[i][1] = self.player_list[i-1][1]

        # Check if player reached goal
        if self.player_list[0][0] == self.goal_row and self.player_list[0][1] == self.goal_col:
            print("Goal Reached")
            self.player_list.append([last_row, last_col])
            self.game_continue = False
            if len(self.player_list) == ROWS * COLS:
                self.game_won = True
                if not auto_run:
                    self.unbind("<Up>")
                    self.unbind("<Down>")
                    self.unbind("<Left>")
                    self.unbind("<Right>")
            else:
                self.spawn_goal()  # Spawn new goal

        self.last_direction = (dr, dc)
        self.canvas.delete("player")
        self.player = self.draw_player(self.player_list)
        if self.game_won:
            self.show_win()  # Draw after player so overlay is on top

    def spawn_goal(self):
        """Create goal in random location not on player."""

        # Remove old goal if it exists
        if self.goal:
            self.canvas.delete(self.goal)

        # Pick random free cell
        while True:
            r = random.randint(0, ROWS - 1)
            c = random.randint(0, COLS - 1)

            # Avoid spawning on player
            covered = False
            for row, col in self.player_list:
                if r == row and c == col:
                    covered = True
            if not covered:
                break

        # Store goal position
        self.goal_row = r
        self.goal_col = c

        # Draw goal rectangle
        x1 = c * CELL_SIZE + 15
        y1 = r * CELL_SIZE + 15
        x2 = x1 + CELL_SIZE - 30
        y2 = y1 + CELL_SIZE - 30

        self.goal = self.canvas.create_rectangle(x1, y1, x2, y2, fill="red")

    def show_game_over(self):
        """Draw Game Over overlay on the canvas."""
        w = COLS * CELL_SIZE
        h = ROWS * CELL_SIZE
        margin = 40
        # Dark overlay rectangle
        self.canvas.create_rectangle(
            margin, margin, w - margin, h - margin,
            fill="black", outline="white", width=3, tags="game_over"
        )
        # Game Over text
        self.canvas.create_text(
            w // 2, h // 2,
            text="Game Over",
            fill="white", font=("Arial", 24, "bold"), tags="game_over"
        )
        self.canvas.create_text(
            w // 2, h // 2 + 32,
            text="Snake hit its own body",
            fill="lightgray", font=("Arial", 12), tags="game_over"
        )

    def show_win(self):
        """Draw win overlay on the canvas."""
        w = COLS * CELL_SIZE
        h = ROWS * CELL_SIZE
        margin = 40
        self.canvas.create_rectangle(
            margin, margin, w - margin, h - margin,
            fill="darkgreen", outline="gold", width=3, tags="game_win"
        )
        self.canvas.create_text(
            w // 2, h // 2,
            text="You Win!",
            fill="gold", font=("Arial", 24, "bold"), tags="game_win"
        )
        self.canvas.create_text(
            w // 2, h // 2 + 32,
            text="Board complete!",
            fill="lightgreen", font=("Arial", 12), tags="game_win"
        )

    def get_occupied_spaces(self):
        """Return set of occupied grid cells (player + goal)."""
        return {
            (self.player_list[0][0],self.player_list[0][1]),
            (self.goal_row, self.goal_col)
        }

    def update_loop(self):
        """Continuously prints occupied spaces."""
        if self.game_over or self.game_won:
            return
        if self.game_continue:
            return

        if auto_run:
             self.move_player(0, 0)

        occupied = self.get_occupied_spaces()
        print("Occupied:", occupied)

        # Call update_loop again after TICK_MS
        self.after(TICK_MS, self.update_loop)


# Run game
if __name__ == "__main__":
    game = GameGrid()
    print(game.get_occupied_spaces())  # Show starting occupied spaces
    game.mainloop()
