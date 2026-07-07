const canvas = document.querySelector("#gameBoard");
const context = canvas.getContext("2d");
const scoreElement = document.querySelector("#score");
const bestScoreElement = document.querySelector("#bestScore");
const statusElement = document.querySelector("#status");
const pauseButton = document.querySelector("#pauseButton");
const restartButton = document.querySelector("#restartButton");
const controlButtons = document.querySelectorAll("[data-direction]");

const cellSize = 24;
const tileCount = canvas.width / cellSize;
const tickDelay = 120;

const directions = {
  up: { x: 0, y: -1 },
  down: { x: 0, y: 1 },
  left: { x: -1, y: 0 },
  right: { x: 1, y: 0 },
};

const keyToDirection = {
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
let bestScore = Number(localStorage.getItem("snakeBestScore")) || 0;
let gameTimer;
let isPaused;
let isGameOver;

function startGame() {
  snake = [
    { x: 9, y: 10 },
    { x: 8, y: 10 },
    { x: 7, y: 10 },
  ];
  direction = directions.right;
  nextDirection = directions.right;
  score = 0;
  isPaused = false;
  isGameOver = false;
  food = createFood();

  updateHud();
  updatePauseButton();
  setStatus("Ешь красные яблоки и не врезайся в стены или хвост.");
  clearInterval(gameTimer);
  gameTimer = setInterval(updateGame, tickDelay);
  drawGame();
}

function updateGame() {
  if (isPaused || isGameOver) {
    return;
  }

  direction = nextDirection;

  const head = snake[0];
  const nextHead = {
    x: head.x + direction.x,
    y: head.y + direction.y,
  };

  if (hitsWall(nextHead) || hitsSnake(nextHead)) {
    endGame();
    return;
  }

  snake.unshift(nextHead);

  if (nextHead.x === food.x && nextHead.y === food.y) {
    score += 1;
    food = createFood();
    updateHud();
  } else {
    snake.pop();
  }

  drawGame();
}

function drawGame() {
  context.clearRect(0, 0, canvas.width, canvas.height);
  drawBoard();
  drawFood();
  drawSnake();
}

function drawBoard() {
  context.fillStyle = "#0c1117";
  context.fillRect(0, 0, canvas.width, canvas.height);

  context.strokeStyle = "rgba(255, 255, 255, 0.035)";
  context.lineWidth = 1;

  for (let position = 0; position <= canvas.width; position += cellSize) {
    context.beginPath();
    context.moveTo(position, 0);
    context.lineTo(position, canvas.height);
    context.stroke();

    context.beginPath();
    context.moveTo(0, position);
    context.lineTo(canvas.width, position);
    context.stroke();
  }
}

function drawSnake() {
  snake.forEach((part, index) => {
    const inset = index === 0 ? 2 : 3;
    context.fillStyle = index === 0 ? "#9ff0ca" : "#39b87f";
    roundRect(
      part.x * cellSize + inset,
      part.y * cellSize + inset,
      cellSize - inset * 2,
      cellSize - inset * 2,
      6,
    );
  });
}

function drawFood() {
  const centerX = food.x * cellSize + cellSize / 2;
  const centerY = food.y * cellSize + cellSize / 2;

  context.fillStyle = "#f05d5e";
  context.beginPath();
  context.arc(centerX, centerY, cellSize * 0.36, 0, Math.PI * 2);
  context.fill();

  context.fillStyle = "#ffd166";
  context.fillRect(centerX - 2, centerY - 12, 4, 6);
}

function roundRect(x, y, width, height, radius) {
  context.beginPath();
  context.roundRect(x, y, width, height, radius);
  context.fill();
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

function changeDirection(directionName) {
  const newDirection = directions[directionName];
  const isOpposite =
    newDirection.x + direction.x === 0 && newDirection.y + direction.y === 0;

  if (!isOpposite) {
    nextDirection = newDirection;
  }
}

function togglePause() {
  if (isGameOver) {
    return;
  }

  isPaused = !isPaused;
  updatePauseButton();
  setStatus(isPaused ? "Пауза. Нажми пробел, чтобы продолжить." : "Игра продолжается.");
}

function endGame() {
  isGameOver = true;
  clearInterval(gameTimer);
  bestScore = Math.max(bestScore, score);
  localStorage.setItem("snakeBestScore", bestScore);
  updateHud();
  setStatus("Игра окончена. Нажми ↻ или Enter, чтобы начать заново.");
}

function updateHud() {
  scoreElement.textContent = score;
  bestScoreElement.textContent = bestScore;
}

function updatePauseButton() {
  pauseButton.querySelector("span").textContent = isPaused ? "▶" : "II";
  pauseButton.setAttribute("aria-label", isPaused ? "Продолжить" : "Пауза");
}

function setStatus(message) {
  statusElement.textContent = message;
}

document.addEventListener("keydown", (event) => {
  if (event.code === "Space") {
    event.preventDefault();
    togglePause();
    return;
  }

  if (event.code === "Enter" && isGameOver) {
    startGame();
    return;
  }

  const directionName = keyToDirection[event.code];

  if (directionName) {
    event.preventDefault();
    changeDirection(directionName);
  }
});

pauseButton.addEventListener("click", togglePause);
restartButton.addEventListener("click", startGame);

controlButtons.forEach((button) => {
  button.addEventListener("click", () => {
    changeDirection(button.dataset.direction);
  });
});

startGame();
