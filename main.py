import json
import time
import tkinter as tk

from datetime import date
from pathlib import Path
from collections import deque

import psutil


# -------------------- SETTINGS --------------------

LIMIT_SECONDS = 90 * 60
CHECK_INTERVAL = 60
WARNING_MINUTES = [20, 10, 5]

APP_DIR = Path.home() / "CS2TimeLimiter"
STATE_FILE = APP_DIR / "state.json"

GAMES = {
    "CS2": "cs2.exe",
    "Rocket League": "RocketLeague.exe",
}


# -------------------- STATE MANAGEMENT --------------------

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

        if STATE_FILE.exists():
            try:
                data = json.loads(
                    STATE_FILE.read_text(encoding="utf-8")
                )

                if data.get("date") == self.today():

                    if "used_seconds" in data:
                        used_seconds = float(
                            data.get("used_seconds", 0)
                        )

                    elif isinstance(data.get("games"), dict):
                        used_seconds = sum(
                            max(0, float(value))
                            for value in data["games"].values()
                        )

                    else:
                        used_seconds = 0

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
                            max(0, used_seconds),
                        ),
                        "warnings_sent": list(set(warnings_sent)),
                    }

            except (ValueError, OSError, TypeError):
                pass

        return self.default_state()

    def save_state(self, state):
        APP_DIR.mkdir(parents=True, exist_ok=True)

        STATE_FILE.write_text(
            json.dumps(state, indent=2),
            encoding="utf-8",
        )


# -------------------- GAME PROCESS MANAGEMENT --------------------

class GameManager:
    def find_processes(self, executable):
        processes = []

        for process in psutil.process_iter(["name"]):
            try:
                process_name = process.info["name"] or ""

                if process_name.lower() == executable.lower():
                    processes.append(process)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return processes

    def find_all_games(self):
        return {
            game_name: self.find_processes(executable)
            for game_name, executable in GAMES.items()
        }

    def close_game(self, processes):
        processes = list(processes)

        for process in processes:
            try:
                process.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        _, still_running = psutil.wait_procs(
            processes,
            timeout=3,
        )

        for process in still_running:
            try:
                process.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def close_all_games(self):
        for executable in GAMES.values():
            self.close_game(self.find_processes(executable))


# -------------------- NOTIFICATIONS --------------------

class NotificationManager:
    def __init__(self, root):
        self.root = root
        self.current_popup = None
        self.pending_notifications = deque()

    def notify(self, title, message):
        self.pending_notifications.append((title, message))
        self.show_next_popup()

    def show_next_popup(self):
        if self.current_popup is not None:
            return

        if not self.pending_notifications:
            return

        title, message = self.pending_notifications.popleft()

        popup = tk.Toplevel(self.root)
        self.current_popup = popup

        popup.title(title)
        popup.geometry("400x200")
        popup.resizable(False, False)
        popup.attributes("-topmost", True)
        popup.configure(bg="#20242c")

        def close_popup():
            if self.current_popup is popup:
                self.current_popup = None

            popup.destroy()
            self.root.after(150, self.show_next_popup)

        popup.protocol("WM_DELETE_WINDOW", close_popup)

        tk.Label(
            popup,
            text=title,
            font=("Segoe UI", 15, "bold"),
            fg="white",
            bg="#20242c",
            wraplength=360,
        ).pack(pady=(22, 10))

        tk.Label(
            popup,
            text=message,
            font=("Segoe UI", 11),
            fg="#e0e0e0",
            bg="#20242c",
            wraplength=350,
            justify="center",
        ).pack(pady=5)

        tk.Button(
            popup,
            text="OK, understood",
            font=("Segoe UI", 10, "bold"),
            command=close_popup,
            padx=14,
            pady=5,
        ).pack(pady=14)

        popup.update_idletasks()

        x = (
            popup.winfo_screenwidth() - popup.winfo_width()
        ) // 2
        y = (
            popup.winfo_screenheight() - popup.winfo_height()
        ) // 2

        popup.geometry(f"+{x}+{y}")
        popup.lift()
        popup.focus_force()


# -------------------- MAIN TIMER --------------------

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

    def format_time(self, seconds):
        total_seconds = max(0, int(seconds))
        minutes = total_seconds // 60
        seconds_remaining = total_seconds % 60

        return f"{minutes} min {seconds_remaining} sec"

    def check_games(self):
        # Reset the shared allowance at local midnight.
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
            # Enforce the limit if a game is launched again.
            if any_game_running:
                self.game_manager.close_all_games()

        elif any_game_running:
            # Count time only once, even if both games are running.
            self.state["used_seconds"] = min(
                LIMIT_SECONDS,
                self.state["used_seconds"] + elapsed,
            )

            remaining = LIMIT_SECONDS - self.state["used_seconds"]

            # Show each warning only once per day.
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

        # Continue checking even when neither game is running.
        self.root.after(
            CHECK_INTERVAL * 1000,
            self.check_games,
        )


# -------------------- START APPLICATION --------------------

def main():
    root = tk.Tk()
    root.withdraw()

    state_manager = StateManager()
    game_manager = GameManager()
    notification_manager = NotificationManager(root)

    limiter = GameTimeLimiter(
        root,
        state_manager,
        game_manager,
        notification_manager,
    )

    print("Game Time Limiter is running.")
    print(f"Shared daily limit: {LIMIT_SECONDS // 60} minutes.")
    print("Games monitored: CS2 and Rocket League.")

    root.after(1000, limiter.check_games)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Game Time Limiter stopped.")