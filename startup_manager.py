
import sys
from pathlib import Path

import win32com.client


class StartupManager:
    def __init__(self):
        self.startup_folder = (
            Path.home()
            / "AppData"
            / "Roaming"
            / "Microsoft"
            / "Windows"
            / "Start Menu"
            / "Programs"
            / "Startup"
        )

        self.shortcut_path = (
            self.startup_folder / "Game Time Limiter.lnk"
        )

        # The main.py file is in the same directory as this file.
        self.script_path = (
            Path(__file__).resolve().with_name("main.py")
        )

    def is_enabled(self):
        return self.shortcut_path.exists()

    def enable(self):
        self.startup_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Use the Python interpreter running this application.
        python_executable = Path(sys.executable).resolve()

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(self.shortcut_path))

        shortcut.Targetpath = str(python_executable)
        shortcut.Arguments = f'"{self.script_path}"'
        shortcut.WorkingDirectory = str(self.script_path.parent)
        shortcut.Description = "Game Time Limiter"
        shortcut.save()

    def disable(self):
        if self.shortcut_path.exists():
            self.shortcut_path.unlink()
