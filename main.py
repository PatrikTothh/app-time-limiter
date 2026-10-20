
import tkinter as tk

from config import LIMIT_SECONDS
from state_manager import StateManager
from game_manager import GameManager
from notification_manager import NotificationManager
from game_time_limiter import GameTimeLimiter
from settings_window import SettingsWindow


def main():
    root = tk.Tk()
    root.title("Game Time Limiter")
    root.geometry("350x220")
    root.resizable(False, False)

    state_manager = StateManager()
    game_manager = GameManager()
    notification_manager = NotificationManager(root)

    limiter = GameTimeLimiter(
        root,
        state_manager,
        game_manager,
        notification_manager,
    )

    # Main application window
    tk.Label(
        root,
        text="Game Time Limiter",
        font=("Segoe UI", 16, "bold"),
    ).pack(pady=(20, 10))

    tk.Label(
        root,
        text=f"Shared daily limit: {LIMIT_SECONDS // 60} minutes",
        font=("Segoe UI", 10),
    ).pack(pady=5)

    tk.Button(
        root,
        text="Settings",
        font=("Segoe UI", 10),
        width=18,
        command=lambda: SettingsWindow(root),
    ).pack(pady=10)

    tk.Label(
        root,
        text="Monitoring CS2 and Rocket League",
        font=("Segoe UI", 9),
        fg="gray",
    ).pack(pady=5)

    print("Game Time Limiter is running.")
    print(f"Shared daily limit: {LIMIT_SECONDS // 60} minutes.")
    print("Games monitored: CS2 and Rocket League.")

    # Start checking games after one second.
    root.after(1000, limiter.check_games)

    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Game Time Limiter stopped.")
