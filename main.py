from game_engine.engine import GameEngine
from game_logic.game_logic import DeliriumLogic
from runners.contracts.runner_server_abc import RunnerServerABC
import sys


def get_runner(location: str) -> RunnerServerABC:
    if location == "local":
        from runners.local.runner_server import LocalRunnerServer

        return LocalRunnerServer()
    else:
        from runners.cloud.runner_server import CloudRunnerServer

        return CloudRunnerServer()


if __name__ == "__main__":

    game_location = sys.argv[1] if len(sys.argv) > 1 else "local"

    runner = get_runner(game_location)

    game_logic = DeliriumLogic()
    game_engine = GameEngine(game_logic, app_runner=runner, new_game=True)
    game_engine.play_game()
