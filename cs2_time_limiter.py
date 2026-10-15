
import json
import time
import tkinter as tk
from datetime import date
from pathlib import Path
from collections import deque

import psutil


# -------------------- SETTINGS --------------------

# One shared daily limit for BOTH games
LIMIT_SECONDS = 90 * 60  # 15 minutes

# Check running games every second
CHECK_INTERVAL = 60

# Popup warnings when this many minutes remain
WARNING_MINUTES = [20, 10, 5]

APP_DIR = Path.home() / "CS2TimeLimiter"
STATE_FILE = APP_DIR / "state.json"

GAMES = {
    "CS2": "cs2.exe",
    "Rocket League": "RocketLeague.exe",
}


# -------------------- STATE MANAGEMENT --------------------

def today():
    return date.today().isoformat()


def load_state():
    APP_DIR.mkdir(parents=True, exist_ok=True)

    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))

            if data.get("date") == today():

                # Current shared-timer format
                if "used_seconds" in data:
                    used_seconds = float(data.get("used_seconds", 0))

                # Migrate from the previous two-game timer format
                elif isinstance(data.get("games"), dict):
                    used_seconds = sum(
                        max(0, float(value))
                        for value in data["games"].values()
                    )

                else:
                    used_seconds = 0

                old_warnings = data.get("warnings_sent", [])

                # Support the previous format where warnings were
                # stored separately for each game.
                if isinstance(old_warnings, dict):
                    old_warnings = [
                        minute
                        for game_warnings in old_warnings.values()
                        if isinstance(game_warnings, list)
                        for minute in game_warnings
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
                    "date": today(),
                    "used_seconds": min(
                        LIMIT_SECONDS,
                        max(0, used_seconds),
                    ),
                    "warnings_sent": list(set(warnings_sent)),
                }

        except (ValueError, OSError, TypeError):
            pass

    return {
        "date": today(),
        "used_seconds": 0,
        "warnings_sent": [],
    }


def save_state():
    APP_DIR.mkdir(parents=True, exist_ok=True)

    STATE_FILE.write_text(
        json.dumps(state, indent=2),
        encoding="utf-8",
    )


# -------------------- GAME PROCESS MANAGEMENT --------------------

def find_processes(executable):
    processes = []

    for process in psutil.process_iter(["name"]):
        try:
            process_name = process.info["name"] or ""

            if process_name.lower() == executable.lower():
                processes.append(process)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return processes


def find_all_games():
    running_games = {}

    for game_name, executable in GAMES.items():
        running_games[game_name] = find_processes(executable)

    return running_games


def close_game(processes):
    for process in processes:
        try:
            process.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    _, still_running = psutil.wait_procs(processes, timeout=3)

    for process in still_running:
        try:
            process.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def close_all_games():
    for executable in GAMES.values():
        close_game(find_processes(executable))


# -------------------- POPUP WINDOWS --------------------

root = None
current_popup = None
pending_notifications = deque()


def notify(title, message):
    """Queue a popup to display on the screen."""
    pending_notifications.append((title, message))
    show_next_popup()


def show_next_popup():
    global current_popup

    if current_popup is not None:
        return

    if not pending_notifications:
        return

    title, message = pending_notifications.popleft()

    popup = tk.Toplevel(root)
    current_popup = popup

    popup.title(title)
    popup.geometry("400x200")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)
    popup.configure(bg="#20242c")

    def close_popup():
        global current_popup

        if current_popup is popup:
            current_popup = None

        popup.destroy()

        # Display the next queued warning, if there is one.
        root.after(150, show_next_popup)

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

    x = (popup.winfo_screenwidth() - popup.winfo_width()) // 2
    y = (popup.winfo_screenheight() - popup.winfo_height()) // 2

    popup.geometry(f"+{x}+{y}")
    popup.lift()
    popup.focus_force()


# -------------------- TIMER --------------------

state = load_state()


def format_time(seconds):
    total_seconds = max(0, int(seconds))
    minutes = total_seconds // 60
    seconds_remaining = total_seconds % 60

    return f"{minutes} min {seconds_remaining} sec"


def check_games():
    global state

    # Reset the shared allowance at local midnight.
    if state["date"] != today():
        state = {
            "date": today(),
            "used_seconds": 0,
            "warnings_sent": [],
        }

        save_state()

        notify(
            "Daily game timer reset",
            f"Your shared {LIMIT_SECONDS // 60}-minute allowance is available again.",
        )

    running_games = find_all_games()

    any_game_running = any(
        processes for processes in running_games.values()
    )

    now = time.monotonic()
    elapsed = max(0, now - check_games.last_tick)
    check_games.last_tick = now

    if state["used_seconds"] >= LIMIT_SECONDS:
        # Enforce the limit even if a game is launched again.
        if any_game_running:
            close_all_games()

    elif any_game_running:
        # Count time only once, even if BOTH games are running.
        state["used_seconds"] = min(
            LIMIT_SECONDS,
            state["used_seconds"] + elapsed,
        )

        remaining = LIMIT_SECONDS - state["used_seconds"]

        # Show each warning only once per day.
        for minutes in WARNING_MINUTES:
            if (
                remaining <= minutes * 60
                and minutes not in state["warnings_sent"]
            ):
                state["warnings_sent"].append(minutes)

                notify(
                    f"{minutes} minutes remaining",
                    f"You have {minutes} minutes left in your "
                    "shared daily gaming allowance for CS2 "
                    "and Rocket League.",
                )

        if state["used_seconds"] >= LIMIT_SECONDS:
            state["used_seconds"] = LIMIT_SECONDS
            save_state()

            close_all_games()

            notify(
                "Daily game limit reached",
                f"Your shared {LIMIT_SECONDS // 60}-minute limit has been reached. "
                "CS2 and Rocket League have been closed.",
            )

    save_state()

    # Keep checking, even when neither game is running.
    root.after(CHECK_INTERVAL * 1000, check_games)


check_games.last_tick = time.monotonic()


# -------------------- START APPLICATION --------------------

def main():
    global root

    root = tk.Tk()
    root.withdraw()

    print("Game Time Limiter is running.")
    print(f"Shared daily limit: {LIMIT_SECONDS // 60} minutes.")
    print("Games monitored: CS2 and Rocket League.")

    root.after(1000, check_games)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Game Time Limiter stopped.")
