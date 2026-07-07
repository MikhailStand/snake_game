import curses
import random
import time


MAX_WIDTH = 30
MAX_HEIGHT = 18
MIN_WIDTH = 12
MIN_HEIGHT = 8
TICK_SECONDS = 0.11

SNAKE_CHAR = "O"
HEAD_CHAR = "@"
FOOD_CHAR = "*"

DIRECTIONS = {
    curses.KEY_UP: (0, -1),
    curses.KEY_DOWN: (0, 1),
    curses.KEY_LEFT: (-1, 0),
    curses.KEY_RIGHT: (1, 0),
    ord("w"): (0, -1),
    ord("W"): (0, -1),
    ord("s"): (0, 1),
    ord("S"): (0, 1),
    ord("a"): (-1, 0),
    ord("A"): (-1, 0),
    ord("d"): (1, 0),
    ord("D"): (1, 0),
}


class SnakeGame:
    def __init__(self, screen):
        self.screen = screen
        self.best_score = 0
        self.rows = 0
        self.cols = 0
        self.width = 0
        self.height = 0
        self.too_small = False
        self.reset()

    def reset(self):
        self.configure_board()
        if self.too_small:
            self.snake = []
            self.food = (0, 0)
            return

        start_x = self.width // 2
        start_y = self.height // 2
        self.snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.paused = False
        self.game_over = False
        self.food = self.create_food()

    def create_food(self):
        while True:
            food = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            if food not in self.snake:
                return food

    def change_direction(self, new_direction):
        dx, dy = self.direction
        new_dx, new_dy = new_direction

        if dx + new_dx == 0 and dy + new_dy == 0:
            return

        self.next_direction = new_direction

    def update(self):
        self.configure_board()

        if self.too_small or self.paused or self.game_over:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        if self.hits_wall(new_head) or new_head in self.snake:
            self.game_over = True
            self.best_score = max(self.best_score, self.score)
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.best_score = max(self.best_score, self.score)
            self.food = self.create_food()
        else:
            self.snake.pop()

    def hits_wall(self, point):
        x, y = point
        return x < 0 or y < 0 or x >= self.width or y >= self.height

    def draw(self):
        self.screen.erase()
        if self.too_small:
            self.draw_too_small_message()
            self.screen.refresh()
            return

        self.draw_header()
        self.draw_border()
        self.draw_food()
        self.draw_snake()
        self.draw_footer()
        self.screen.refresh()

    def configure_board(self):
        rows, cols = self.screen.getmaxyx()
        if rows == self.rows and cols == self.cols:
            return

        self.rows = rows
        self.cols = cols
        self.width = min(MAX_WIDTH, max(0, cols - 2))
        self.height = min(MAX_HEIGHT, max(0, rows - 5))
        self.too_small = self.width < MIN_WIDTH or self.height < MIN_HEIGHT

        if not self.too_small and hasattr(self, "snake") and self.snake:
            self.snake = [
                (min(x, self.width - 1), min(y, self.height - 1)) for x, y in self.snake
            ]
            if self.food[0] >= self.width or self.food[1] >= self.height:
                self.food = self.create_food()

    def safe_addstr(self, y, x, text):
        if y < 0 or x < 0 or y >= self.rows or x >= self.cols:
            return

        visible_text = text[: self.cols - x - 1]
        if not visible_text:
            return

        try:
            self.screen.addstr(y, x, visible_text)
        except curses.error:
            pass

    def draw_too_small_message(self):
        self.safe_addstr(0, 0, "Terminal is too small for Snake.")
        self.safe_addstr(1, 0, "Make the Codespaces terminal bigger.")
        self.safe_addstr(2, 0, f"Current: {self.cols}x{self.rows}")
        self.safe_addstr(3, 0, f"Need at least: {MIN_WIDTH + 2}x{MIN_HEIGHT + 5}")
        self.safe_addstr(5, 0, "Press Q to quit.")

    def draw_header(self):
        self.safe_addstr(0, 0, f"Snake | Score: {self.score} | Best: {self.best_score}")

    def draw_border(self):
        top = "+" + "-" * self.width + "+"
        self.safe_addstr(1, 0, top)

        for y in range(self.height):
            self.safe_addstr(y + 2, 0, "|")
            self.safe_addstr(y + 2, self.width + 1, "|")

        self.safe_addstr(self.height + 2, 0, top)

    def draw_food(self):
        food_x, food_y = self.food
        self.safe_addstr(food_y + 2, food_x + 1, FOOD_CHAR)

    def draw_snake(self):
        for index, (x, y) in enumerate(self.snake):
            char = HEAD_CHAR if index == 0 else SNAKE_CHAR
            self.safe_addstr(y + 2, x + 1, char)

    def draw_footer(self):
        if self.game_over:
            message = "Game over. Press Enter to restart or Q to quit."
        elif self.paused:
            message = "Paused. Press Space to continue."
        else:
            message = "Arrows/WASD: move | Space: pause | Q: quit"

        self.safe_addstr(self.height + 4, 0, message)

    def handle_key(self, key):
        if key in (ord("q"), ord("Q")):
            return False

        if key == ord(" "):
            if not self.game_over:
                self.paused = not self.paused
            return True

        if key in (curses.KEY_ENTER, 10, 13):
            if self.game_over:
                self.reset()
            return True

        if key in DIRECTIONS:
            self.change_direction(DIRECTIONS[key])

        return True


def run(screen):
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    screen.nodelay(True)
    screen.keypad(True)
    screen.timeout(0)

    game = SnakeGame(screen)
    running = True

    while running:
        key = screen.getch()
        if key != -1:
            running = game.handle_key(key)

        game.update()
        game.draw()
        time.sleep(TICK_SECONDS)


if __name__ == "__main__":
    curses.wrapper(run)
