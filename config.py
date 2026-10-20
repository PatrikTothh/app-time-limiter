
import json
from pathlib import Path


APP_DIR = Path.home() / "CS2TimeLimiter"
STATE_FILE = APP_DIR / "state.json"
SETTINGS_FILE = APP_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "daily_limit_minutes": 100,
    "check_interval_seconds": 1,
    "warning_minutes": [45, 30, 15, 5],
    "games": {
        "CS2": "cs2.exe",
        "Rocket League": "RocketLeague.exe",
    },
}


class ConfigManager:
    def __init__(self):
        self.settings = self.load_settings()

    @property
    def limit_seconds(self):
        return self.settings["daily_limit_minutes"] * 60

    def load_settings(self):
        APP_DIR.mkdir(parents=True, exist_ok=True)

        try:
            with SETTINGS_FILE.open("r", encoding="utf-8") as file:
                saved = json.load(file)

            settings = DEFAULT_SETTINGS.copy()
            settings.update({
                key: saved[key]
                for key in DEFAULT_SETTINGS
                if key in saved
            })

            settings["games"] = DEFAULT_SETTINGS["games"].copy()
            if isinstance(saved.get("games"), dict):
                settings["games"].update(saved["games"])

            self._validate(settings)
            return settings

        except FileNotFoundError:
            self._save_defaults()
            return {
                **DEFAULT_SETTINGS,
                "warning_minutes": DEFAULT_SETTINGS["warning_minutes"].copy(),
                "games": DEFAULT_SETTINGS["games"].copy(),
            }

        except (json.JSONDecodeError, TypeError, ValueError, KeyError):
            self._save_defaults()
            return {
                **DEFAULT_SETTINGS,
                "warning_minutes": DEFAULT_SETTINGS["warning_minutes"].copy(),
                "games": DEFAULT_SETTINGS["games"].copy(),
            }

    def save_settings(self, new_settings):
        settings = {
            **self.settings,
            **new_settings,
        }

        settings["games"] = {
            **self.settings["games"],
            **new_settings.get("games", {}),
        }

        self._validate(settings)

        APP_DIR.mkdir(parents=True, exist_ok=True)

        with SETTINGS_FILE.open("w", encoding="utf-8") as file:
            json.dump(settings, file, indent=4)

        self.settings = settings

    def _validate(self, settings):
        limit = settings["daily_limit_minutes"]
        interval = settings["check_interval_seconds"]
        warnings = settings["warning_minutes"]
        games = settings["games"]

        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
            raise ValueError("Daily limit must be a positive whole number.")

        if (
            not isinstance(interval, int)
            or isinstance(interval, bool)
            or not 1 <= interval <= 60
        ):
            raise ValueError("Check interval must be between 1 and 60 seconds.")

        if (
            not isinstance(warnings, list)
            or any(
                not isinstance(value, int)
                or isinstance(value, bool)
                or value <= 0
                or value >= limit
                for value in warnings
            )
            or len(warnings) != len(set(warnings))
        ):
            raise ValueError(
                "Warnings must be unique positive whole minutes, "
                "smaller than the daily limit."
            )

        if not isinstance(games, dict):
            raise ValueError("Game settings are invalid.")

        for name in DEFAULT_SETTINGS["games"]:
            executable = games.get(name)
            if not isinstance(executable, str) or not executable.strip():
                raise ValueError(f"Executable name for {name} cannot be empty.")

    def _save_defaults(self):
        APP_DIR.mkdir(parents=True, exist_ok=True)
        with SETTINGS_FILE.open("w", encoding="utf-8") as file:
            json.dump(DEFAULT_SETTINGS, file, indent=4)
