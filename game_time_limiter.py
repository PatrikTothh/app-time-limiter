
import time

from config import ConfigManager


class GameTimeLimiter:
    def __init__(
        self,
        root,
        state_manager,
        game_manager,
        notification_manager,
        config_manager,
    ):
        self.root = root
        self.state_manager = state_manager
        self.game_manager = game_manager
        self.notification_manager = notification_manager
        self.config_manager = config_manager

        self.state = self.state_manager.load_state()
        self.last_tick = time.monotonic()

    def check_games(self):
        # Read the latest settings each time the timer runs.
        limit_seconds = self.config_manager.limit_seconds
        warning_minutes = self.config_manager.settings["warning_minutes"]
        check_interval = self.config_manager.settings[
            "check_interval_seconds"
        ]

        # Reset the allowance when a new day begins.
        if self.state["date"] != self.state_manager.today():
            self.state = self.state_manager.default_state()
            self.state_manager.save_state(self.state)

            self.notification_manager.notify(
                "Daily game timer reset",
                f"Your shared {limit_seconds // 60}-minute "
                "allowance is available again.",
            )

        # Check whether either game is running.
        running_games = self.game_manager.find_all_games()

        any_game_running = any(
            processes for processes in running_games.values()
        )

        now = time.monotonic()
        elapsed = max(0, now - self.last_tick)
        self.last_tick = now

        if self.state["used_seconds"] >= limit_seconds:
            if any_game_running:
                self.game_manager.close_all_games()

        elif any_game_running:
            # Count time once, even if both games are running.
            self.state["used_seconds"] = min(
                limit_seconds,
                self.state["used_seconds"] + elapsed,
            )

            remaining = limit_seconds - self.state["used_seconds"]

            # Display each warning only once per day.
            for minutes in warning_minutes:
                if (
                    remaining <= minutes * 60
                    and minutes not in self.state["warnings_sent"]
                ):
                    self.state["warnings_sent"].append(minutes)

                    self.notification_manager.notify(
                        f"{minutes} minutes remaining",
                        f"You have {minutes} minutes left in your "
                        "shared daily gaming allowance for CS2 "
                        "and Rocket League.",
                    )

            # Close both games when the allowance is exhausted.
            if self.state["used_seconds"] >= limit_seconds:
                self.state["used_seconds"] = limit_seconds
                self.game_manager.close_all_games()

                self.notification_manager.notify(
                    "Daily game limit reached",
                    f"Your shared {limit_seconds // 60}-minute "
                    "limit has been reached. CS2 and Rocket "
                    "League have been closed.",
                )

        self.state_manager.save_state(self.state)

        # Schedule the next check using the configured interval.
        self.root.after(
            check_interval * 1000,
            self.check_games,
        )
