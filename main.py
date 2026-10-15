import tkinter as tk

from state_manager import StateManager
from game_manager import GameManager
from notification_manager import NotificationManager
from game_time_limiter import GameTimeLimiter


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
    print("Shared daily limit: 90 minutes.")
    print("Games monitored: CS2 and Rocket League.")

    root.after(1000, limiter.check_games)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Game Time Limiter stopped.")