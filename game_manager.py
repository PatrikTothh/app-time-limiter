
import psutil


class GameManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager

    def find_processes(self, executable):
        """Find running processes matching an executable name."""
        found = []

        for process in psutil.process_iter(["name"]):
            try:
                process_name = process.info["name"]

                if (
                    process_name
                    and process_name.lower() == executable.lower()
                ):
                    found.append(process)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return found

    def find_all_games(self):
        """Return running processes grouped by configured game name."""
        games = self.config_manager.settings["games"]
        found = {}

        for game_name, executable in games.items():
            processes = self.find_processes(executable)

            if processes:
                found[game_name] = processes

        return found

    def close_game(self, processes):
        """Terminate game processes, then force-kill any that remain."""
        for process in processes:
            try:
                process.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        for process in processes:
            try:
                process.wait(timeout=3)
            except psutil.TimeoutExpired:
                try:
                    process.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def close_all_games(self):
        """Close all games currently configured and running."""
        running_games = self.find_all_games()

        for processes in running_games.values():
            self.close_game(processes)
