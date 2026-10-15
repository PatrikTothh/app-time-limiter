import psutil

from config import GAMES


class GameManager:
    def find_processes(self, executable):
        processes = []

        for process in psutil.process_iter(["name"]):
            try:
                name = process.info["name"] or ""

                if name.lower() == executable.lower():
                    processes.append(process)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return processes

    def find_all_games(self):
        return {
            game: self.find_processes(executable)
            for game, executable in GAMES.items()
        }

    def close_game(self, processes):
        processes = list(processes)

        for process in processes:
            try:
                process.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        _, still_running = psutil.wait_procs(
            processes,
            timeout=3,
        )

        for process in still_running:
            try:
                process.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def close_all_games(self):
        for executable in GAMES.values():
            self.close_game(self.find_processes(executable))