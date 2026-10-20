
import tkinter as tk
from tkinter import messagebox

from startup_manager import StartupManager


class SettingsWindow:
    def __init__(self, root, config_manager):
        self.root = root
        self.config_manager = config_manager
        self.startup_manager = StartupManager()

        self.window = tk.Toplevel(root)
        self.window.title("Game Time Limiter Settings")
        self.window.geometry("440x430")
        self.window.resizable(False, False)

        settings = self.config_manager.settings

        tk.Label(
            self.window,
            text="Settings",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=(12, 8))

        frame = tk.Frame(self.window, padx=20)
        frame.pack(fill="x")

        self.limit_var = tk.StringVar(
            value=str(settings["daily_limit_minutes"])
        )
        self.interval_var = tk.StringVar(
            value=str(settings["check_interval_seconds"])
        )
        self.warnings_var = tk.StringVar(
            value=", ".join(map(str, settings["warning_minutes"]))
        )
        self.cs2_var = tk.StringVar(value=settings["games"]["CS2"])
        self.rocket_var = tk.StringVar(
            value=settings["games"]["Rocket League"]
        )

        self.add_setting(
            frame, "Daily time limit (minutes):", self.limit_var
        )
        self.add_setting(
            frame, "Check interval (seconds):", self.interval_var
        )
        self.add_setting(
            frame, "Warnings (minutes remaining):", self.warnings_var
        )
        self.add_setting(
            frame, "CS2 executable:", self.cs2_var
        )
        self.add_setting(
            frame, "Rocket League executable:", self.rocket_var
        )

        self.startup_var = tk.BooleanVar(
            master=self.window,
            value=self.startup_manager.is_enabled(),
        )

        tk.Checkbutton(
            self.window,
            text="Start with Windows",
            variable=self.startup_var,
            command=self.toggle_startup,
            font=("Segoe UI", 10),
        ).pack(pady=(10, 5))

        tk.Button(
            self.window,
            text="Save settings",
            width=18,
            command=self.save_settings,
        ).pack(pady=8)

    def add_setting(self, parent, label_text, variable):
        row = tk.Frame(parent)
        row.pack(fill="x", pady=4)

        tk.Label(
            row,
            text=label_text,
            anchor="w",
            font=("Segoe UI", 9),
        ).pack(fill="x")

        tk.Entry(
            row,
            textvariable=variable,
            font=("Segoe UI", 10),
        ).pack(fill="x", pady=(2, 0))

    def save_settings(self):
        try:
            limit = int(self.limit_var.get().strip())
            interval = int(self.interval_var.get().strip())

            warning_text = self.warnings_var.get().strip()
            warnings = []

            if warning_text:
                warnings = [
                    int(value.strip())
                    for value in warning_text.split(",")
                ]

            games = {
                "CS2": self.cs2_var.get().strip(),
                "Rocket League": self.rocket_var.get().strip(),
            }

            self.config_manager.save_settings({
                "daily_limit_minutes": limit,
                "check_interval_seconds": interval,
                "warning_minutes": warnings,
                "games": games,
            })

            messagebox.showinfo(
                "Settings saved",
                "Your settings have been saved.",
                parent=self.window,
            )

        except (ValueError, TypeError) as error:
            messagebox.showerror(
                "Invalid settings",
                str(error) or "Please check the values you entered.",
                parent=self.window,
            )

        except OSError as error:
            messagebox.showerror(
                "Save error",
                f"Could not save settings:\n{error}",
                parent=self.window,
            )

    def toggle_startup(self):
        try:
            if self.startup_var.get():
                self.startup_manager.enable()
            else:
                self.startup_manager.disable()

        except Exception as error:
            self.startup_var.set(self.startup_manager.is_enabled())
            messagebox.showerror(
                "Startup setting error",
                f"Could not update the startup setting:\n{error}",
                parent=self.window,
            )
