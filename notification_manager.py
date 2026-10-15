import tkinter as tk
from collections import deque


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