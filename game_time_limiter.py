import time

from config import (
    LIMIT_SECONDS,
    CHECK_INTERVAL,
    WARNING_MINUTES,
)


class GameTimeLimiter:
    def __init__(
        self,
        root,
        state_manager,
        game_manager,
        notification_manager,
    ):
        self.root = root
        self.state_manager = state_manager
        self.game_manager = game_manager
        self.notifications = notification_manager

        self.state = self.state_manager.load_state()
        self.last_tick = time.monotonic()

    def check_games(self):
        if self.state["date"] != self.state_manager.today():
            self.state = self.state_manager.default_state()
            self.state_manager.save_state(self.state)

            self.notifications.notify(
                "Daily game timer reset",
                f"Your shared {LIMIT_SECONDS // 60}-minute "
                "allowance is available again.",
            )

        running_games = self.game_manager.find_all_games()

        any_game_running = any(
            processes for processes in running_games.values()
        )

        now = time.monotonic()
        elapsed = max(0, now - self.last_tick)
        self.last_tick = now

        if self.state["used_seconds"] >= LIMIT_SECONDS:
            if any_game_running:
                self.game_manager.close_all_games()

        elif any_game_running:
            self.state["used_seconds"] = min(
                LIMIT_SECONDS,
                self.state["used_seconds"] + elapsed,
            )

            remaining = LIMIT_SECONDS - self.state["used_seconds"]

            for minutes in WARNING_MINUTES:
                if (
                    remaining <= minutes * 60
                    and minutes not in self.state["warnings_sent"]
                ):
                    self.state["warnings_sent"].append(minutes)

                    self.notifications.notify(
                        f"{minutes} minutes remaining",
                        f"You have {minutes} minutes left in your "
                        "shared daily gaming allowance for CS2 "
                        "and Rocket League.",
                    )

            if self.state["used_seconds"] >= LIMIT_SECONDS:
                self.state["used_seconds"] = LIMIT_SECONDS
                self.state_manager.save_state(self.state)

                self.game_manager.close_all_games()

                self.notifications.notify(
                    "Daily game limit reached",
                    f"Your shared {LIMIT_SECONDS // 60}-minute "
                    "limit has been reached. CS2 and Rocket "
                    "League have been closed.",
                )

        self.state_manager.save_state(self.state)

        self.root.after(
            CHECK_INTERVAL * 1000,
            self.check_games,
        )