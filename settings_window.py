
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from pathlib import Path

from startup_manager import StartupManager


class ManageAppsWindow:
    def __init__(self, root, config_manager):
        self.config_manager = config_manager

        self.window = tk.Toplevel(root)
        self.window.title("Manage Limited Apps")
        self.window.geometry("430x370")
        self.window.resizable(False, False)

        tk.Label(
            self.window,
            text="Limited Applications",
            font=("Segoe UI", 15, "bold"),
        ).pack(pady=(15, 5))

        tk.Label(
            self.window,
            text="Applications in this list share your daily time allowance.",
            font=("Segoe UI", 9),
            wraplength=380,
        ).pack(pady=(0, 10))

        self.app_list = tk.Listbox(
            self.window,
            font=("Segoe UI", 10),
            height=10,
            width=48,
            selectmode=tk.SINGLE,
        )
        self.app_list.pack(
            padx=15,
            fill="both",
            expand=True,
        )

        buttons = tk.Frame(self.window)
        buttons.pack(pady=12)

        tk.Button(
            buttons,
            text="Add app",
            width=12,
            command=self.add_app,
        ).pack(side="left", padx=5)

        tk.Button(
            buttons,
            text="Remove selected",
            width=15,
            command=self.remove_app,
        ).pack(side="left", padx=5)

        self.refresh_list()

    def refresh_list(self):
        self.app_list.delete(0, tk.END)

        for name, executable in self.config_manager.settings["games"].items():
            self.app_list.insert(
                tk.END,
                f"{name}  —  {executable}",
            )

    def add_app(self):
        # Open the Windows file picker to select an executable.
        file_path = filedialog.askopenfilename(
            parent=self.window,
            title="Select an application executable",
            filetypes=[
                ("Executable files", "*.exe"),
                ("All files", "*.*"),
            ],
        )

        if not file_path:
            return

        executable_path = Path(file_path)
        executable = executable_path.name

        # Prevent the same executable filename being added twice.
        games = self.config_manager.settings["games"]

        for name, existing_executable in games.items():
            if existing_executable.lower() == executable.lower():
                messagebox.showwarning(
                    "Application already exists",
                    f"{name} already uses {executable}.",
                    parent=self.window,
                )
                return

        # Suggest a display name based on the selected filename.
        suggested_name = executable_path.stem

        name = simpledialog.askstring(
            "Application name",
            "Enter a display name for this application:",
            initialvalue=suggested_name,
            parent=self.window,
        )

        if name is None:
            return

        name = name.strip()

        if not name:
            messagebox.showerror(
                "Invalid name",
                "Please enter an application name.",
                parent=self.window,
            )
            return

        # Prevent duplicate display names.
        if name in games:
            messagebox.showerror(
                "Application already exists",
                "An application with this name is already in the list.",
                parent=self.window,
            )
            return

        updated_games = dict(games)
        updated_games[name] = executable

        try:
            self.config_manager.save_settings({
                "games": updated_games,
            })
        except (ValueError, OSError) as error:
            messagebox.showerror(
                "Could not add application",
                str(error),
                parent=self.window,
            )
            return

        self.refresh_list()

    def remove_app(self):
        selection = self.app_list.curselection()

        if not selection:
            messagebox.showwarning(
                "No application selected",
                "Select an application you want to remove.",
                parent=self.window,
            )
            return

        names = list(self.config_manager.settings["games"].keys())
        name = names[selection[0]]

        confirm = messagebox.askyesno(
            "Remove application",
            f"Remove {name} from the limited applications list?",
            parent=self.window,
        )

        if not confirm:
            return

        updated_games = dict(self.config_manager.settings["games"])
        del updated_games[name]

        try:
            self.config_manager.save_settings({
                "games": updated_games,
            })
        except (ValueError, OSError) as error:
            messagebox.showerror(
                "Could not remove application",
                str(error),
                parent=self.window,
            )
            return

        self.refresh_list()


class SettingsWindow:
    def __init__(self, root, config_manager):
        self.root = root
        self.config_manager = config_manager
        self.startup_manager = StartupManager()
        self.apps_window = None

        self.window = tk.Toplevel(root)
        self.window.title("Game Time Limiter Settings")
        self.window.geometry("440x465")
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

        self.add_setting(
            frame,
            "Daily time limit (minutes):",
            self.limit_var,
        )

        self.add_setting(
            frame,
            "Check interval (seconds):",
            self.interval_var,
        )

        self.add_setting(
            frame,
            "Warnings (minutes remaining):",
            self.warnings_var,
        )

        tk.Button(
            self.window,
            text="Manage Limited Apps",
            width=22,
            command=self.open_manage_apps,
        ).pack(pady=(12, 5))

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
        ).pack(pady=5)

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

    def open_manage_apps(self):
        # Reuse the existing application-management window if open.
        if self.apps_window is not None:
            try:
                if self.apps_window.window.winfo_exists():
                    self.apps_window.window.deiconify()
                    self.apps_window.window.lift()
                    self.apps_window.window.focus_force()
                    return
            except tk.TclError:
                pass

        self.apps_window = ManageAppsWindow(
            self.window,
            self.config_manager,
        )

    def save_settings(self):
        try:
            limit = int(self.limit_var.get().strip())
            interval = int(self.interval_var.get().strip())

            warning_text = self.warnings_var.get().strip()

            if warning_text:
                warnings = [
                    int(value.strip())
                    for value in warning_text.split(",")
                ]
            else:
                warnings = []

            self.config_manager.save_settings({
                "daily_limit_minutes": limit,
                "check_interval_seconds": interval,
                "warning_minutes": warnings,
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
            self.startup_var.set(
                self.startup_manager.is_enabled()
            )

            messagebox.showerror(
                "Startup setting error",
                f"Could not update the startup setting:\n{error}",
                parent=self.window,
            )
