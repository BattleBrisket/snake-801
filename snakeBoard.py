
import tkinter as tk
import random
from collections import deque

# Grid settings
grid_size = 6
ROWS = grid_size
COLS = grid_size
CELL_SIZE = 60   # Pixel size of each grid square

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

        # Start update loop
        self.update_loop()

    def draw_player(self, player_list):
        """Draw player circle in grid cell."""
        canvas_drawn = []
        for coord in player_list:
            x1 = coord[1] * CELL_SIZE + 10
            y1 = coord[0] * CELL_SIZE + 10
            x2 = x1 + CELL_SIZE - 20
            y2 = y1 + CELL_SIZE - 20
            canvas_drawn.append(self.canvas.create_oval(x1, y1, x2, y2, fill="blue", tags="player"))
        return canvas_drawn

    def move_player(self, dr, dc):
        """Move player if inside grid boundaries."""

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
            self.player_list.append([last_row,last_col])
            self.game_continue = False
            self.spawn_goal()  # Spawn new goal

        self.canvas.delete("player")
        self.player = self.draw_player(self.player_list)

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

    def get_occupied_spaces(self):
        """Return set of occupied grid cells (player + goal)."""
        return {
            (self.player_list[0][0],self.player_list[0][1]),
            (self.goal_row, self.goal_col)
        }

    def update_loop(self):
        """Continuously prints occupied spaces."""
        if self.game_continue:
            return

        if auto_run:
             self.move_player(0, 0)

        occupied = self.get_occupied_spaces()
        print("Occupied:", occupied)

        # Call update_loop again after 600 ms
        self.after(600, self.update_loop)


# Run game
if __name__ == "__main__":
    game = GameGrid()
    print(game.get_occupied_spaces())  # Show starting occupied spaces
    game.mainloop()
