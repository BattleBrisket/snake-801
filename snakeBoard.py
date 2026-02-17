import tkinter as tk
import random

# Grid settings
grid_size = 6
ROWS = grid_size
COLS = grid_size
CELL_SIZE = 60   # Pixel size of each grid square


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

        # Player starting position (row, column)
        self.player_row = 2
        self.player_col = 2

        # Goal state variables
        self.goal_row = None
        self.goal_col = None
        self.goal = None
        self.spawn_goal()  # Create first goal

        # Draw player on screen
        self.player = self.draw_player(self.player_row, self.player_col)

        # Bind arrow keys to player movement
        self.bind("<Up>", lambda e: self.move_player(-1, 0))
        self.bind("<Down>", lambda e: self.move_player(1, 0))
        self.bind("<Left>", lambda e: self.move_player(0, -1))
        self.bind("<Right>", lambda e: self.move_player(0, 1))

        # Controls whether update loop continues
        self.game_continue = False

        # Start update loop
        self.update_loop()

    def draw_player(self, row, col):
        """Draw player circle in grid cell."""
        x1 = col * CELL_SIZE + 10
        y1 = row * CELL_SIZE + 10
        x2 = x1 + CELL_SIZE - 20
        y2 = y1 + CELL_SIZE - 20
        return self.canvas.create_oval(x1, y1, x2, y2, fill="blue")

    def move_player(self, dr, dc):
        """Move player if inside grid boundaries."""

        # Calculate new position
        new_row = self.player_row + dr
        new_col = self.player_col + dc

        # Stop movement if hitting window border
        if not (0 <= new_row < ROWS and 0 <= new_col < COLS):
            print("hit window barrier!")
            return

        # Move player drawing
        dx = dc * CELL_SIZE
        dy = dr * CELL_SIZE
        self.canvas.move(self.player, dx, dy)

        # Update stored player position
        self.player_row = new_row
        self.player_col = new_col

        # Check if player reached goal
        if self.player_row == self.goal_row and self.player_col == self.goal_col:
            print("Goal Reached")
            self.game_continue = False
            self.spawn_goal()  # Spawn new goal

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
            if r != self.player_row or c != self.player_col:
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

    def get_occupied_spaces(self):
        """Return set of occupied grid cells (player + goal)."""
        return {
            (self.player_row, self.player_col),
            (self.goal_row, self.goal_col)
        }

    def update_loop(self):
        """Continuously prints occupied spaces."""
        if self.game_continue:
            return

        occupied = self.get_occupied_spaces()
        print("Occupied:", occupied)

        # Call update_loop again after 600 ms
        self.after(600, self.update_loop)


# Run game
if __name__ == "__main__":
    game = GameGrid()
    print(game.get_occupied_spaces())  # Show starting occupied spaces
    game.mainloop()
