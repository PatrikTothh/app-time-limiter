
import tkinter as tk
from tkinter import simpledialog, messagebox

import pystray
from PIL import Image, ImageDraw

from settings_window import SettingsWindow


class TrayManager:
    def __init__(self, root):
        self.root = root
        self.icon = None
        self.settings_window = None

    def create_icon_image(self):
        """Create a simple custom icon for the system tray."""
        image = Image.new("RGB", (64, 64), "#20242c")
        draw = ImageDraw.Draw(image)

        # Clock face
        draw.ellipse(
            (8, 8, 56, 56),
            fill="#3b82f6",
        )

        # Clock hands
        draw.line(
            (32, 32, 32, 18),
            fill="white",
            width=4,
        )
        draw.line(
            (32, 32, 43, 38),
            fill="white",
            width=4,
        )

        return image

    def show_window(self, icon=None, item=None):
        """Show and focus the main application window."""
        self.root.after(0, self._show_window)

    def _show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def open_settings(self, icon=None, item=None):
        """Open the settings window on the Tkinter thread."""
        self.root.after(0, self._open_settings)

    
    def open_settings(self, icon=None, item=None):
        """Open Settings, reusing the existing window if possible."""
        self.root.after(0, self._open_settings)


    
    def _open_settings(self):
        # Reuse an existing Settings window if it is already open.
        if self.settings_window is not None:
            try:
                if self.settings_window.window.winfo_exists():
                    self.settings_window.window.deiconify()
                    self.settings_window.window.lift()
                    self.settings_window.window.focus_force()
                    return
            except tk.TclError:
                pass

        # Ask for the password before opening Settings.
        if not self.ask_for_password():
            return

        self.settings_window = SettingsWindow(self.root)



    def hide_window(self):
        self.root.withdraw()

    def exit_application(self, icon=None, item=None):
        """Stop the tray icon and close the application."""
        self.root.after(0, self._exit_application)

    def _exit_application(self):
        if self.icon is not None:
            self.icon.stop()

        self.root.destroy()

    def start(self):
        """Start the tray icon without blocking Tkinter."""
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

        # Run the tray icon alongside Tkinter's event loop.
        self.icon.run_detached()
    
    def ask_for_password(self):
        password = simpledialog.askstring(
            "Settings password",
            "Enter the password to access Settings:",
            show="*",
            parent=self.root,
        )

        if password is None:
            return False

        # Temporary password; change this before using the app.
        correct_password = "Password123"

        if password == correct_password:
            return True

        messagebox.showerror(
            "Access denied",
            "Incorrect password.",
            parent=self.root,
        )
        return False

