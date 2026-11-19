import sys
import tkinter as tk

from board import Board


class Game:
    def __init__(self):
        self.board = Board()

        self.previous_grid = None
        self.previous_score = 0

        self.best_score = self.board.score

        self.message = ""

    def display(self):
        print("\n" + "+------+------+------+------+")

        for row in self.board.grid:
            print(
                "|"
                + "|".join(
                    f"{x:^6}" if x else f"{' ':^6}"
                    for x in row
                )
                + "|"
            )

            print("+------+------+------+------+")

        print("Score:", self.board.score, " Best:", self.best_score)

    def has_won(self):
        return any(2048 in row for row in self.board.grid)

    def is_game_over(self):
        return not self.board.can_move()

    def move(self, key):
        moves = {
            "a": self.board.move_left,
            "d": self.board.move_right,
            "w": self.board.move_up,
            "s": self.board.move_down
        }

        if key not in moves:
            self.message = "Invalid command."
            return False

        old_grid = [row[:] for row in self.board.grid]
        old_score = self.board.score

        changed = moves[key]()

        if not changed:
            self.message = "No tiles moved."
            return False

        self.previous_grid = old_grid
        self.previous_score = old_score

        self.board.add_random_tile()

        self.best_score = max(
            self.best_score,
            self.board.score
        )

        self.message = "Move successful."

        return True

    def undo(self):
        if self.previous_grid is None:
            self.message = "Nothing to undo."
            return False

        self.board.grid = [
            row[:]
            for row in self.previous_grid
        ]

        self.board.score = self.previous_score

        self.previous_grid = None
        self.previous_score = 0

        self.message = "Undo successful."

        return True

    def run(self):
        print("2048 — W/A/S/D to move, U to undo, Q to quit.")

        while True:
            self.display()

            if self.has_won():
                print("You reached 2048!")
                return

            if self.is_game_over():
                print("No legal moves remain.")
                return

            key = input("> ").strip().lower()

            if key == "q":
                return

            if key == "u":
                self.undo()

                if self.message:
                    print(self.message)
                    self.message = ""

                continue

            if key not in "wasd":
                print("Invalid command.")
                continue

            if self.move(key):
                if self.message:
                    print(self.message)
                    self.message = ""


class GameUI:
    COLORS = {
        0: "#cdc1b4",
        2: "#eee4da",
        4: "#ede0c8",
        8: "#f2b179",
        16: "#f59563",
        32: "#f67c5f",
        64: "#f65e3b",
        128: "#edcf72",
        256: "#edcc61",
        512: "#edc850",
        1024: "#edc53f",
        2048: "#edc22e",
    }

    def __init__(self, root=None):
        self.root = root or tk.Tk()
        self.root.title("2048")
        self.root.configure(bg="#faf8ef")
        self.root.resizable(False, False)
        self.root.bind("<KeyPress>", self.handle_key)

        self.game = Game()
        self.status_text = tk.StringVar(value="Use arrow keys or WASD to play.")
        self.score_text = tk.StringVar(value="Score: 0")
        self.best_text = tk.StringVar(value="Best: 0")

        self.build_ui()
        self.refresh_board()

    def build_ui(self):
        main = tk.Frame(self.root, bg="#faf8ef", padx=20, pady=20)
        main.pack(fill="both", expand=True)

        top_bar = tk.Frame(main, bg="#faf8ef")
        top_bar.pack(fill="x")

        title = tk.Label(
            top_bar,
            text="2048",
            fg="#776e65",
            bg="#faf8ef",
            font=("Verdana", 42, "bold"),
            anchor="w",
        )
        title.pack(side="left")

        score_frame = tk.Frame(top_bar, bg="#bbada0", padx=12, pady=8)
        score_frame.pack(side="right", padx=(10, 0))
        tk.Label(
            score_frame,
            textvariable=self.score_text,
            fg="#ffffff",
            bg="#bbada0",
            font=("Verdana", 12, "bold"),
        ).pack()

        best_frame = tk.Frame(top_bar, bg="#bbada0", padx=12, pady=8)
        best_frame.pack(side="right", padx=(10, 0))
        tk.Label(
            best_frame,
            textvariable=self.best_text,
            fg="#ffffff",
            bg="#bbada0",
            font=("Verdana", 12, "bold"),
        ).pack()

        controls = tk.Frame(main, bg="#faf8ef")
        controls.pack(fill="x", pady=(12, 0))

        tk.Button(controls, text="New Game", command=self.restart, width=12, bg="#8f7a66", fg="white",
                  activebackground="#7d695c", activeforeground="white", font=("Verdana", 10, "bold")).pack(side="left")
        tk.Button(controls, text="Undo", command=self.undo_move, width=10, bg="#8f7a66", fg="white",
                  activebackground="#7d695c", activeforeground="white", font=("Verdana", 10, "bold")).pack(side="left", padx=(10, 0))

        status = tk.Label(
            main,
            textvariable=self.status_text,
            fg="#776e65",
            bg="#faf8ef",
            font=("Verdana", 11, "bold"),
            justify="left",
            anchor="w",
        )
        status.pack(fill="x", pady=(12, 10))

        board = tk.Frame(main, bg="#bbada0", padx=12, pady=12)
        board.pack(fill="both")

        self.cells = []
        for row in range(4):
            row_cells = []
            for col in range(4):
                cell = tk.Label(
                    board,
                    width=6,
                    height=3,
                    bd=0,
                    relief="flat",
                    bg="#cdc1b4",
                    fg="#776e65",
                    font=("Verdana", 20, "bold"),
                    text="",
                    anchor="center",
                )
                cell.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
                row_cells.append(cell)
            self.cells.append(row_cells)

        for i in range(4):
            board.grid_columnconfigure(i, weight=1)
            board.grid_rowconfigure(i, weight=1)

    def _tile_color(self, value):
        if value == 0:
            return "#cdc1b4"
        if value in self.COLORS:
            return self.COLORS[value]
        return "#3c3a32"

    def _text_color(self, value):
        return "#776e65" if value <= 4 else "#f9f6f2"

    def handle_key(self, event):
        key_map = {
            "Left": "a",
            "Right": "d",
            "Up": "w",
            "Down": "s",
        }

        key = key_map.get(event.keysym)
        if key is None:
            if event.keysym.lower() == "u":
                self.undo_move()
            return

        self.process_move(key)

    def process_move(self, key):
        if self.game.move(key):
            if self.game.has_won():
                self.status_text.set("You reached 2048! You win!")
            elif self.game.is_game_over():
                self.status_text.set("No legal moves remain. Game over!")
            else:
                self.status_text.set(self.game.message)
        else:
            self.status_text.set(self.game.message)

        self.refresh_board()

    def undo_move(self):
        if self.game.undo():
            self.status_text.set(self.game.message)
        else:
            self.status_text.set(self.game.message)
        self.refresh_board()

    def restart(self):
        self.game = Game()
        self.status_text.set("New game started. Use arrow keys or WASD to play.")
        self.refresh_board()

    def refresh_board(self):
        for r in range(4):
            for c in range(4):
                value = self.game.board.grid[r][c]
                cell = self.cells[r][c]
                cell.configure(
                    text="" if value == 0 else str(value),
                    bg=self._tile_color(value),
                    fg=self._text_color(value),
                    font=("Verdana", 20 if value < 1024 else 16, "bold"),
                )

        self.score_text.set(f"Score: {self.game.board.score}")
        self.best_text.set(f"Best: {self.game.best_score}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        Game().run()
    else:
        GameUI().run()