
import json
from datetime import date

from config import APP_DIR, STATE_FILE


class StateManager:
    def __init__(self):
        APP_DIR.mkdir(parents=True, exist_ok=True)

    def today(self):
        return date.today().isoformat()

    def default_state(self):
        return {
            "date": self.today(),
            "used_seconds": 0,
            "warnings_sent": [],
        }

    def load_state(self):
        if not STATE_FILE.exists():
            return self.default_state()

        try:
            with STATE_FILE.open("r", encoding="utf-8") as file:
                state = json.load(file)

            if state.get("date") != self.today():
                return self.default_state()

            # Support the current shared-timer state format.
            used_seconds = max(0, float(state.get("used_seconds", 0)))

            warnings_sent = state.get("warnings_sent", [])
            if not isinstance(warnings_sent, list):
                warnings_sent = []

            return {
                "date": self.today(),
                "used_seconds": used_seconds,
                "warnings_sent": warnings_sent,
            }

        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return self.default_state()

    def save_state(self, state):
        APP_DIR.mkdir(parents=True, exist_ok=True)

        with STATE_FILE.open("w", encoding="utf-8") as file:
            json.dump(state, file, indent=4)
