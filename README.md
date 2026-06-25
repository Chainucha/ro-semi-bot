# ro-semi-bot

Semi-automatic bot for **Ragnarok Online**. Drives one or more game
windows with a skill macro, watches the screen for a target pattern via OpenCV
template matching, and pauses with a sound + Telegram alert when something is
detected (e.g. a GM check / captcha). A live terminal dashboard shows per-window
status.

> ⚠️ Automating online games usually violates the game's Terms of Service and may
> get your account banned. Use at your own risk. This project is for educational
> purposes.

## Features

- **Multi-window** — auto-detects every matching game window by title and runs an
  independent bot thread per window.
- **Skill macro** — repeating F1 → click → F2 → Enter loop with randomized
  click offset and timing to look less robotic (`src/macro.py`).
- **Detection** — OpenCV `matchTemplate` against `src/mat/needle.png`; when the
  match score crosses the threshold the bot pauses for safety (`src/detection.py`).
- **Safety response** — on detection: stop macro, bring window to foreground, play
  `src/cops.mp3`, send Telegram message. Auto-resumes after the alert clears.
- **Telegram notifications** — async notifier via `python-telegram-bot`
  (`tools/notification.py`).
- **Live debug dashboard** — boxed per-bot status (window handle, match value,
  detect/macro state) plus CPU/RAM/threads, toggled with F5 (`src/debugger.py`).
- **Input via PostMessage** — keyboard/mouse sent directly to the window handle
  (`tools/input_handler.py`).

## Requirements

- Windows (uses `win32*` APIs, AutoHotkey, ANSI console)
- Python 3.10+
- [AutoHotkey](https://www.autohotkey.com/) installed (the `ahk` library wraps it)

### Python packages

```bash
pip install opencv-python numpy pygame pywin32 ahk python-telegram-bot python-dotenv keyboard psutil pytest
```

## Setup

1. Clone:

   ```bash
   git clone https://github.com/Chainucha/ro-semi-bot.git
   cd ro-semi-bot
   ```

2. (Optional) Telegram alerts — create a `.env` file:

   ```env
   BOT_TOKEN=your_telegram_bot_token
   CHAT_ID=your_chat_id
   ```

   If omitted, the notifier silently disables itself.

3. Set `WINDOW_TITLE` in `main.py` / `tools/window_handler.py` to match your
   game client's window title.

4. Replace `src/mat/needle.png` with the image you want detected (default
   threshold `0.75` in `src/detection.py`).

## Usage

Start the game window(s) first, then:

```bash
python main.py
```

The bot detects all matching windows and starts a thread for each.

### Controls

| Key      | Action                                          |
|----------|-------------------------------------------------|
| `PgUp`   | Start macro + activate bot                      |
| `PgDn`   | Toggle bot active / paused                      |
| `Home`   | Toggle the currently focused window's bot       |
| `End`    | Stop the game loop                              |
| `F5`     | Toggle the debug dashboard                      |
| `Ctrl+C` | Stop all bots and exit                          |

## Project structure

```
main.py                 Entry point: window detection, hotkeys, lifecycle
Bot.py                  Bot + BotManager (threads per window)
src/
  game.py               Per-window state machine, safety logic
  macro.py              Skill rotation loop
  detection.py          OpenCV template matching
  debugger.py           Live terminal dashboard
  mat/needle.png        Detection target image
  cops.mp3              Alert sound
tools/
  window_handler.py     Window lookup / geometry (win32 + ahk)
  window_capture.py     Screenshot capture
  input_handler.py      Keyboard/Mouse via PostMessage
  coordinate_handler.py Coordinate helpers
  notification.py       Telegram notifier
  mouse_blocker.py      Mouse input blocking
  VK_MAP.py             Virtual-key map
tests/
  test_notifier.py
```

## Tests

```bash
pytest
```

## License

See [LICENSE](LICENSE).
