from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os


HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8000"))

PAGE = """<!doctype html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Snake Game</title>
    <style>
      :root {
        --bg: #111827;
        --panel: #1f2937;
        --line: rgba(255, 255, 255, 0.12);
        --text: #f9fafb;
        --muted: #a7b0bf;
        --snake: #22c55e;
        --head: #86efac;
        --food: #ef4444;
      }

      * {
        box-sizing: border-box;
      }

      body {
        min-height: 100vh;
        margin: 0;
        display: grid;
        place-items: center;
        background: var(--bg);
        color: var(--text);
        font-family: Arial, sans-serif;
      }

      main {
        width: min(94vw, 560px);
        display: grid;
        gap: 12px;
        padding: 16px;
      }

      .hud {
        display: grid;
        grid-template-columns: 1fr 1fr 44px 44px;
        gap: 8px;
      }

      .box,
      button {
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--panel);
        color: var(--text);
      }

      .box {
        padding: 10px 12px;
      }

      .label {
        margin: 0 0 4px;
        color: var(--muted);
        font-size: 12px;
        text-transform: uppercase;
      }

      .value {
        margin: 0;
        font-size: 24px;
        font-weight: 800;
      }

      button {
        min-height: 44px;
        cursor: pointer;
        font-size: 18px;
        font-weight: 800;
      }

      canvas {
        width: 100%;
        aspect-ratio: 1;
        display: block;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: #020617;
      }

      .controls {
        width: 174px;
        justify-self: center;
        display: grid;
        grid-template-areas:
          ". up ."
          "left down right";
        grid-template-columns: repeat(3, 54px);
        gap: 6px;
      }

      .control {
        width: 54px;
        height: 54px;
      }

      .up { grid-area: up; }
      .left { grid-area: left; }
      .down { grid-area: down; }
      .right { grid-area: right; }

      .status {
        min-height: 22px;
        margin: 0;
        color: var(--muted);
        text-align: center;
      }

      @media (max-width: 420px) {
        .hud {
          grid-template-columns: 1fr 1fr;
        }
      }
    </style>
  </head>
  <body>
    <main>
      <section class="hud">
        <div class="box">
          <p class="label">Score</p>
          <p class="value" id="score">0</p>
        </div>
        <div class="box">
          <p class="label">Best</p>
          <p class="value" id="best">0</p>
        </div>
        <button id="pause" type="button" aria-label="Pause">II</button>
        <button id="restart" type="button" aria-label="Restart">↻</button>
      </section>

      <canvas id="board" width="480" height="480"></canvas>

      <section class="controls">
        <button class="control up" type="button" data-direction="up">▲</button>
        <button class="control left" type="button" data-direction="left">◀</button>
        <button class="control down" type="button" data-direction="down">▼</button>
        <button class="control right" type="button" data-direction="right">▶</button>
      </section>

      <p class="status" id="status">Use arrows or WASD. Space pauses the game.</p>
    </main>

    <script>
      const canvas = document.querySelector("#board");
      const ctx = canvas.getContext("2d");
      const scoreEl = document.querySelector("#score");
      const bestEl = document.querySelector("#best");
      const statusEl = document.querySelector("#status");
      const pauseButton = document.querySelector("#pause");
      const restartButton = document.querySelector("#restart");

      const cellSize = 24;
      const tileCount = canvas.width / cellSize;
      const tickMs = 120;

      const directions = {
        up: { x: 0, y: -1 },
        down: { x: 0, y: 1 },
        left: { x: -1, y: 0 },
        right: { x: 1, y: 0 },
      };

      const keys = {
        ArrowUp: "up",
        KeyW: "up",
        ArrowDown: "down",
        KeyS: "down",
        ArrowLeft: "left",
        KeyA: "left",
        ArrowRight: "right",
        KeyD: "right",
      };

      let snake;
      let food;
      let direction;
      let nextDirection;
      let score;
      let best = Number(localStorage.getItem("snakeBest")) || 0;
      let paused;
      let gameOver;
      let timerId;

      function startGame() {
        snake = [
          { x: 9, y: 10 },
          { x: 8, y: 10 },
          { x: 7, y: 10 },
        ];
        direction = directions.right;
        nextDirection = directions.right;
        score = 0;
        paused = false;
        gameOver = false;
        food = createFood();
        updateHud();
        updatePauseButton();
        setStatus("Eat the red food and avoid walls and your tail.");
        clearInterval(timerId);
        timerId = setInterval(updateGame, tickMs);
        draw();
      }

      function updateGame() {
        if (paused || gameOver) {
          return;
        }

        direction = nextDirection;

        const head = snake[0];
        const newHead = {
          x: head.x + direction.x,
          y: head.y + direction.y,
        };

        if (hitsWall(newHead) || hitsSnake(newHead)) {
          endGame();
          return;
        }

        snake.unshift(newHead);

        if (newHead.x === food.x && newHead.y === food.y) {
          score += 1;
          best = Math.max(best, score);
          localStorage.setItem("snakeBest", best);
          food = createFood();
          updateHud();
        } else {
          snake.pop();
        }

        draw();
      }

      function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        drawBoard();
        drawFood();
        drawSnake();
      }

      function drawBoard() {
        ctx.fillStyle = "#020617";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.strokeStyle = "rgba(255,255,255,0.05)";

        for (let pos = 0; pos <= canvas.width; pos += cellSize) {
          ctx.beginPath();
          ctx.moveTo(pos, 0);
          ctx.lineTo(pos, canvas.height);
          ctx.stroke();

          ctx.beginPath();
          ctx.moveTo(0, pos);
          ctx.lineTo(canvas.width, pos);
          ctx.stroke();
        }
      }

      function drawSnake() {
        snake.forEach((part, index) => {
          const inset = index === 0 ? 2 : 3;
          ctx.fillStyle = index === 0 ? "#86efac" : "#22c55e";
          ctx.fillRect(
            part.x * cellSize + inset,
            part.y * cellSize + inset,
            cellSize - inset * 2,
            cellSize - inset * 2,
          );
        });
      }

      function drawFood() {
        ctx.fillStyle = "#ef4444";
        ctx.beginPath();
        ctx.arc(
          food.x * cellSize + cellSize / 2,
          food.y * cellSize + cellSize / 2,
          cellSize * 0.35,
          0,
          Math.PI * 2,
        );
        ctx.fill();
      }

      function createFood() {
        let nextFood;
        do {
          nextFood = {
            x: Math.floor(Math.random() * tileCount),
            y: Math.floor(Math.random() * tileCount),
          };
        } while (snake.some((part) => part.x === nextFood.x && part.y === nextFood.y));

        return nextFood;
      }

      function hitsWall(point) {
        return point.x < 0 || point.y < 0 || point.x >= tileCount || point.y >= tileCount;
      }

      function hitsSnake(point) {
        return snake.some((part) => part.x === point.x && part.y === point.y);
      }

      function changeDirection(name) {
        const newDirection = directions[name];
        const opposite =
          newDirection.x + direction.x === 0 && newDirection.y + direction.y === 0;

        if (!opposite) {
          nextDirection = newDirection;
        }
      }

      function togglePause() {
        if (gameOver) {
          return;
        }
        paused = !paused;
        updatePauseButton();
        setStatus(paused ? "Paused." : "Game running.");
      }

      function updatePauseButton() {
        pauseButton.textContent = paused ? "▶" : "II";
      }

      function endGame() {
        gameOver = true;
        clearInterval(timerId);
        setStatus("Game over. Press Enter or ↻ to restart.");
      }

      function updateHud() {
        scoreEl.textContent = score;
        bestEl.textContent = best;
      }

      function setStatus(text) {
        statusEl.textContent = text;
      }

      document.addEventListener("keydown", (event) => {
        if (event.code === "Space") {
          event.preventDefault();
          togglePause();
          return;
        }

        if (event.code === "Enter" && gameOver) {
          startGame();
          return;
        }

        const directionName = keys[event.code];
        if (directionName) {
          event.preventDefault();
          changeDirection(directionName);
        }
      });

      document.querySelectorAll("[data-direction]").forEach((button) => {
        button.addEventListener("click", () => changeDirection(button.dataset.direction));
      });

      pauseButton.addEventListener("click", togglePause);
      restartButton.addEventListener("click", startGame);

      startGame();
    </script>
  </body>
</html>
"""


class SnakeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return

        body = PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def main():
    server = ThreadingHTTPServer((HOST, PORT), SnakeHandler)
    print(f"Snake is running on http://localhost:{PORT}")
    print("In Codespaces, open the forwarded port in the Ports tab.")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
