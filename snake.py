import random
import tkinter as tk


CELL_SIZE = 24
CELL_COUNT = 20
BOARD_SIZE = CELL_SIZE * CELL_COUNT
TICK_MS = 120

BG_COLOR = "#0c1117"
GRID_COLOR = "#18212c"
SNAKE_COLOR = "#39b87f"
SNAKE_HEAD_COLOR = "#9ff0ca"
FOOD_COLOR = "#f05d5e"
TEXT_COLOR = "#f7f2e8"
PANEL_COLOR = "#161b22"

DIRECTIONS = {
    "Up": (0, -1),
    "Down": (0, 1),
    "Left": (-1, 0),
    "Right": (1, 0),
    "w": (0, -1),
    "s": (0, 1),
    "a": (-1, 0),
    "d": (1, 0),
}


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Змейка на Python")
        self.root.resizable(False, False)
        self.root.configure(bg=PANEL_COLOR)

        self.score = 0
        self.best_score = 0
        self.is_paused = False
        self.is_game_over = False
        self.timer_id = None

        self.score_label = tk.Label(
            root,
            text="Счет: 0    Рекорд: 0",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Arial", 16, "bold"),
            pady=12,
        )
        self.score_label.pack()

        self.canvas = tk.Canvas(
            root,
            width=BOARD_SIZE,
            height=BOARD_SIZE,
            bg=BG_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack(padx=16, pady=(0, 12))

        self.status_label = tk.Label(
            root,
            text="Стрелки или WASD - движение. Пробел - пауза.",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Arial", 12),
            pady=8,
        )
        self.status_label.pack()

        self.root.bind("<KeyPress>", self.on_key_press)
        self.start_game()

    def start_game(self):
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)

        self.snake = [(9, 10), (8, 10), (7, 10)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self.create_food()
        self.score = 0
        self.is_paused = False
        self.is_game_over = False

        self.set_status("Ешь красную еду и не врезайся в стены или хвост.")
        self.update_score()
        self.draw()
        self.run_loop()

    def run_loop(self):
        if not self.is_paused and not self.is_game_over:
            self.update_game()

        self.timer_id = self.root.after(TICK_MS, self.run_loop)

    def update_game(self):
        self.direction = self.next_direction

        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        if self.hits_wall(new_head) or new_head in self.snake:
            self.end_game()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.best_score = max(self.best_score, self.score)
            self.food = self.create_food()
            self.update_score()
        else:
            self.snake.pop()

        self.draw()

    def draw(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_food()
        self.draw_snake()

    def draw_grid(self):
        for position in range(0, BOARD_SIZE + 1, CELL_SIZE):
            self.canvas.create_line(position, 0, position, BOARD_SIZE, fill=GRID_COLOR)
            self.canvas.create_line(0, position, BOARD_SIZE, position, fill=GRID_COLOR)

    def draw_snake(self):
        for index, (x, y) in enumerate(self.snake):
            inset = 2 if index == 0 else 3
            color = SNAKE_HEAD_COLOR if index == 0 else SNAKE_COLOR
            self.draw_cell(x, y, color, inset)

    def draw_food(self):
        x, y = self.food
        padding = 5
        self.canvas.create_oval(
            x * CELL_SIZE + padding,
            y * CELL_SIZE + padding,
            (x + 1) * CELL_SIZE - padding,
            (y + 1) * CELL_SIZE - padding,
            fill=FOOD_COLOR,
            outline="",
        )

    def draw_cell(self, x, y, color, inset):
        self.canvas.create_rectangle(
            x * CELL_SIZE + inset,
            y * CELL_SIZE + inset,
            (x + 1) * CELL_SIZE - inset,
            (y + 1) * CELL_SIZE - inset,
            fill=color,
            outline="",
        )

    def create_food(self):
        while True:
            food = (
                random.randint(0, CELL_COUNT - 1),
                random.randint(0, CELL_COUNT - 1),
            )

            if food not in self.snake:
                return food

    def hits_wall(self, point):
        x, y = point
        return x < 0 or y < 0 or x >= CELL_COUNT or y >= CELL_COUNT

    def on_key_press(self, event):
        key = event.keysym

        if key == "space":
            self.toggle_pause()
            return

        if key == "Return" and self.is_game_over:
            self.start_game()
            return

        if key in DIRECTIONS:
            self.change_direction(DIRECTIONS[key])

    def change_direction(self, new_direction):
        dx, dy = self.direction
        new_dx, new_dy = new_direction

        if dx + new_dx == 0 and dy + new_dy == 0:
            return

        self.next_direction = new_direction

    def toggle_pause(self):
        if self.is_game_over:
            return

        self.is_paused = not self.is_paused
        if self.is_paused:
            self.set_status("Пауза. Нажми пробел, чтобы продолжить.")
        else:
            self.set_status("Игра продолжается.")

    def end_game(self):
        self.is_game_over = True
        self.set_status("Игра окончена. Нажми Enter, чтобы начать заново.")

    def update_score(self):
        self.score_label.config(text=f"Счет: {self.score}    Рекорд: {self.best_score}")

    def set_status(self, text):
        self.status_label.config(text=text)


if __name__ == "__main__":
    window = tk.Tk()
    SnakeGame(window)
    window.mainloop()
