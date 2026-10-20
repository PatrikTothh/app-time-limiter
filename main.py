
import tkinter as tk

from config import ConfigManager
from state_manager import StateManager
from game_manager import GameManager
from notification_manager import NotificationManager
from game_time_limiter import GameTimeLimiter
from tray_manager import TrayManager


def main():
    root = tk.Tk()
    root.title("Game Time Limiter")
    root.geometry("350x220")
    root.resizable(False, False)

    config_manager = ConfigManager()
    state_manager = StateManager()
    game_manager = GameManager(config_manager)
    notification_manager = NotificationManager(root)

    limiter = GameTimeLimiter(
        root,
        state_manager,
        game_manager,
        notification_manager,
        config_manager,
    )

    tray_manager = TrayManager(root, config_manager)

    tk.Label(
        root,
        text="Game Time Limiter",
        font=("Segoe UI", 16, "bold"),
    ).pack(pady=(20, 10))

    tk.Label(
        root,
        text=(
            f"Shared daily limit: "
            f"{config_manager.settings['daily_limit_minutes']} minutes"
        ),
        font=("Segoe UI", 10),
    ).pack(pady=5)

    tk.Button(
        root,
        text="Settings",
        font=("Segoe UI", 10),
        width=18,
        command=tray_manager.open_settings,
    ).pack(pady=10)

    tk.Label(
        root,
        text="Monitoring CS2 and Rocket League",
        font=("Segoe UI", 9),
        fg="gray",
    ).pack(pady=5)

    root.protocol(
        "WM_DELETE_WINDOW",
        tray_manager.hide_window,
    )

    print("Game Time Limiter is running.")
    print(
        f"Shared daily limit: "
        f"{config_manager.settings['daily_limit_minutes']} minutes."
    )
    print("Games monitored: CS2 and Rocket League.")
    print("Close the window to minimize to the system tray.")
    print("Use the tray menu to exit the application.")

    tray_manager.start()
    root.after(1000, limiter.check_games)

    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Game Time Limiter stopped.")
