import curses
import random
import time


WIDTH = 30
HEIGHT = 18
TICK_SECONDS = 0.11

SNAKE_CHAR = "O"
HEAD_CHAR = "@"
FOOD_CHAR = "*"
EMPTY_CHAR = " "

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
        self.reset()

    def reset(self):
        start_x = WIDTH // 2
        start_y = HEIGHT // 2
        self.snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.paused = False
        self.game_over = False
        self.food = self.create_food()

    def create_food(self):
        while True:
            food = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
            if food not in self.snake:
                return food

    def change_direction(self, new_direction):
        dx, dy = self.direction
        new_dx, new_dy = new_direction

        if dx + new_dx == 0 and dy + new_dy == 0:
            return

        self.next_direction = new_direction

    def update(self):
        if self.paused or self.game_over:
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
        return x < 0 or y < 0 or x >= WIDTH or y >= HEIGHT

    def draw(self):
        self.screen.erase()
        self.draw_header()
        self.draw_border()
        self.draw_food()
        self.draw_snake()
        self.draw_footer()
        self.screen.refresh()

    def draw_header(self):
        self.screen.addstr(0, 0, f"Snake | Score: {self.score} | Best: {self.best_score}")

    def draw_border(self):
        top = "+" + "-" * WIDTH + "+"
        self.screen.addstr(1, 0, top)

        for y in range(HEIGHT):
            self.screen.addstr(y + 2, 0, "|")
            self.screen.addstr(y + 2, WIDTH + 1, "|")

        self.screen.addstr(HEIGHT + 2, 0, top)

    def draw_food(self):
        food_x, food_y = self.food
        self.screen.addstr(food_y + 2, food_x + 1, FOOD_CHAR)

    def draw_snake(self):
        for index, (x, y) in enumerate(self.snake):
            char = HEAD_CHAR if index == 0 else SNAKE_CHAR
            self.screen.addstr(y + 2, x + 1, char)

    def draw_footer(self):
        if self.game_over:
            message = "Game over. Press Enter to restart or Q to quit."
        elif self.paused:
            message = "Paused. Press Space to continue."
        else:
            message = "Arrows/WASD: move | Space: pause | Q: quit"

        self.screen.addstr(HEIGHT + 4, 0, message)

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
    curses.curs_set(0)
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
