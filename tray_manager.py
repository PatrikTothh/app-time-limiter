
import tkinter as tk
from tkinter import simpledialog, messagebox

import pystray
from PIL import Image, ImageDraw

from settings_window import SettingsWindow
from password_manager import PasswordManager


class TrayManager:
    def __init__(self, root, config_manager):
        self.root = root
        self.config_manager = config_manager
        self.icon = None
        self.settings_window = None
        self.password_manager = PasswordManager()

    def create_icon_image(self):
        image = Image.new("RGB", (64, 64), "#20242c")
        draw = ImageDraw.Draw(image)

        draw.ellipse((8, 8, 56, 56), fill="#3b82f6")
        draw.line((32, 32, 32, 18), fill="white", width=4)
        draw.line((32, 32, 43, 38), fill="white", width=4)

        return image

    def show_window(self, icon=None, item=None):
        self.root.after(0, self._show_window)

    def _show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def open_settings(self, icon=None, item=None):
        self.root.after(0, self._open_settings)

    def ask_for_password(self):
        # First launch: create a password.
        if not self.password_manager.has_password():
            password = simpledialog.askstring(
                "Create password",
                "Create a password for Settings:",
                show="*",
                parent=self.root,
            )

            if password is None:
                return False

            if len(password) < 8:
                messagebox.showerror(
                    "Invalid password",
                    "Password must contain at least 8 characters.",
                    parent=self.root,
                )
                return False

            confirmation = simpledialog.askstring(
                "Confirm password",
                "Enter the password again:",
                show="*",
                parent=self.root,
            )

            if confirmation is None:
                return False

            if password != confirmation:
                messagebox.showerror(
                    "Password mismatch",
                    "The passwords do not match.",
                    parent=self.root,
                )
                return False

            try:
                self.password_manager.set_password(password)
            except OSError as error:
                messagebox.showerror(
                    "Password error",
                    f"Could not save the password:\n{error}",
                    parent=self.root,
                )
                return False

            messagebox.showinfo(
                "Password created",
                "Your Settings password has been created.",
                parent=self.root,
            )
            return True

        # Later attempts: verify the existing password.
        password = simpledialog.askstring(
            "Settings password",
            "Enter your password to access Settings:",
            show="*",
            parent=self.root,
        )

        if password is None:
            return False

        if self.password_manager.verify_password(password):
            return True

        messagebox.showerror(
            "Access denied",
            "Incorrect password.",
            parent=self.root,
        )
        return False

    def _open_settings(self):
        # Require authentication before opening or raising Settings.
        if not self.ask_for_password():
            return

        # Reuse an existing Settings window if it is still open.
        if self.settings_window is not None:
            try:
                if self.settings_window.window.winfo_exists():
                    self.settings_window.window.deiconify()
                    self.settings_window.window.lift()
                    self.settings_window.window.focus_force()
                    return
            except tk.TclError:
                pass

        self.settings_window = SettingsWindow(
            self.root,
            self.config_manager,
)
    def hide_window(self):
        """Hide the main window without stopping the application."""
        self.root.withdraw()

    def exit_application(self, icon=None, item=None):
        self.root.after(0, self._exit_application)

    def _exit_application(self):
        if self.icon is not None:
            self.icon.stop()

        self.root.destroy()

    def start(self):
        menu = pystray.Menu(
            pystray.MenuItem(
                "Open Game Time Limiter",
                self.show_window,
                default=True,
            ),
            pystray.MenuItem(
                "Settings",
                self.open_settings,
            ),
            pystray.MenuItem(
                "Exit",
                self.exit_application,
            ),
        )

        self.icon = pystray.Icon(
            "GameTimeLimiter",
            self.create_icon_image(),
            "Game Time Limiter",
            menu,
        )

        self.icon.run_detached()
