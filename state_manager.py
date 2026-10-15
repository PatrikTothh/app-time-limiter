import json
from datetime import date

from config import (
    APP_DIR,
    STATE_FILE,
    LIMIT_SECONDS,
    WARNING_MINUTES,
)


class StateManager:
    def today(self):
        return date.today().isoformat()

    def default_state(self):
        return {
            "date": self.today(),
            "used_seconds": 0,
            "warnings_sent": [],
        }

    def load_state(self):
        APP_DIR.mkdir(parents=True, exist_ok=True)

        if not STATE_FILE.exists():
            return self.default_state()

        try:
            data = json.loads(
                STATE_FILE.read_text(encoding="utf-8")
            )

            if data.get("date") != self.today():
                return self.default_state()

            if "used_seconds" in data:
                used = float(data.get("used_seconds", 0))

            elif isinstance(data.get("games"), dict):
                used = sum(
                    max(0, float(value))
                    for value in data["games"].values()
                )

            else:
                used = 0

            old_warnings = data.get("warnings_sent", [])

            if isinstance(old_warnings, dict):
                old_warnings = [
                    minute
                    for warnings in old_warnings.values()
                    if isinstance(warnings, list)
                    for minute in warnings
                ]

            warnings_sent = []

            if isinstance(old_warnings, list):
                for minute in old_warnings:
                    try:
                        minute = int(minute)
                        if minute in WARNING_MINUTES:
                            warnings_sent.append(minute)
                    except (ValueError, TypeError):
                        pass

            return {
                "date": self.today(),
                "used_seconds": min(
                    LIMIT_SECONDS,
                    max(0, used),
                ),
                "warnings_sent": list(set(warnings_sent)),
            }

        except (ValueError, OSError, TypeError):
            return self.default_state()

    def save_state(self, state):
        APP_DIR.mkdir(parents=True, exist_ok=True)

        STATE_FILE.write_text(
            json.dumps(state, indent=2),
            encoding="utf-8",
        )