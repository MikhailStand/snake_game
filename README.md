# snake_game

Простая игра "Змейка" на Python, которая запускается прямо в терминале.

## Запуск

```bash
python3 snake.py
```

Если команда `python3` не работает, попробуй:

```bash
python snake.py
```

## Управление

- Стрелки или `WASD` - движение
- Пробел - пауза
- `Enter` - начать заново после проигрыша
- `Q` - выйти из игры

## Почему не tkinter?

В GitHub Codespaces обычно нет графического экрана, поэтому `tkinter` падает с ошибкой
`no display name and no $DISPLAY environment variable`. Эта версия использует `curses`,
поэтому работает в терминале Codespaces.
