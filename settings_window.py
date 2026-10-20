
import tkinter as tk
from tkinter import messagebox

from startup_manager import StartupManager


class SettingsWindow:
    def __init__(self, root):
        self.root = root
        self.startup_manager = StartupManager()

        self.window = tk.Toplevel(root)
        self.window.title("Game Time Limiter Settings")
        self.window.geometry("380x200")
        self.window.resizable(False, False)

        tk.Label(
            self.window,
            text="Settings",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=(20, 12))

        self.startup_var = tk.BooleanVar(
            master=self.window,
            value=self.startup_manager.is_enabled(),
        )

        tk.Checkbutton(
            self.window,
            text="Start with Windows",
            variable=self.startup_var,
            command=self.toggle_startup,
            font=("Segoe UI", 11),
        ).pack(pady=10)

    def toggle_startup(self):
        try:
            if self.startup_var.get():
                self.startup_manager.enable()
            else:
                self.startup_manager.disable()

        except Exception as error:
            self.startup_var.set(
                self.startup_manager.is_enabled()
            )

            messagebox.showerror(
                "Startup setting error",
                f"Could not update the startup setting:\n{error}",
                parent=self.window,
            )
