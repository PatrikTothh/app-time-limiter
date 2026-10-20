
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

        if not SETTINGS_FILE.exists():
            self._save_defaults()
            return {
                **DEFAULT_SETTINGS,
                "warning_minutes": DEFAULT_SETTINGS["warning_minutes"].copy(),
                "games": DEFAULT_SETTINGS["games"].copy(),
            }

        try:
            with SETTINGS_FILE.open("r", encoding="utf-8") as file:
                saved = json.load(file)

            settings = {
                "daily_limit_minutes": saved.get(
                    "daily_limit_minutes",
                    DEFAULT_SETTINGS["daily_limit_minutes"],
                ),
                "check_interval_seconds": saved.get(
                    "check_interval_seconds",
                    DEFAULT_SETTINGS["check_interval_seconds"],
                ),
                "warning_minutes": saved.get(
                    "warning_minutes",
                    DEFAULT_SETTINGS["warning_minutes"].copy(),
                ),
                "games": saved.get(
                    "games",
                    DEFAULT_SETTINGS["games"].copy(),
                ),
            }

            self._validate(settings)
            return settings

        except (
            OSError,
            json.JSONDecodeError,
            TypeError,
            ValueError,
            KeyError,
        ):
            # If the configuration is invalid, restore defaults.
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

        # Replace the application list completely when supplied.
        # This allows applications to be removed.
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

        if (
            not isinstance(limit, int)
            or isinstance(limit, bool)
            or limit < 1
        ):
            raise ValueError(
                "Daily limit must be a positive whole number."
            )

        if (
            not isinstance(interval, int)
            or isinstance(interval, bool)
            or not 1 <= interval <= 60
        ):
            raise ValueError(
                "Check interval must be between 1 and 60 seconds."
            )

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
                "Warnings must be unique positive whole minutes "
                "smaller than the daily limit."
            )

        if not isinstance(games, dict):
            raise ValueError("The limited applications list is invalid.")

        for name, executable in games.items():
            if (
                not isinstance(name, str)
                or not name.strip()
                or not isinstance(executable, str)
                or not executable.strip()
            ):
                raise ValueError(
                    "Each application needs a name and executable filename."
                )

            if "/" in executable or "\\" in executable:
                raise ValueError(
                    f"Enter only the executable filename for {name}, "
                    "for example game.exe, not a full path."
                )

    def _save_defaults(self):
        APP_DIR.mkdir(parents=True, exist_ok=True)

        with SETTINGS_FILE.open("w", encoding="utf-8") as file:
            json.dump(DEFAULT_SETTINGS, file, indent=4)
