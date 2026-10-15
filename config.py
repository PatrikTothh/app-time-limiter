from pathlib import Path

LIMIT_SECONDS = 90 * 60
CHECK_INTERVAL = 60
WARNING_MINUTES = [20, 10, 5]

APP_DIR = Path.home() / "CS2TimeLimiter"
STATE_FILE = APP_DIR / "state.json"

GAMES = {
    "CS2": "cs2.exe",
    "Rocket League": "RocketLeague.exe",
}