from game_engine.engine import GameEngine
from game_contracts.runner_server_abc import RunnerServerABC
import sys
import argparse
import importlib

registered_games = {"delirium": "game_logic.game_logic.DeliriumLogic"}


def get_runner(location: str) -> RunnerServerABC:
    if location == "local":
        from runners.local.runner_server import LocalRunnerServer

        return LocalRunnerServer()
    else:
        from runners.cloud.runner_server import CloudRunnerServer

        return CloudRunnerServer()


def load_game_logic(game_name: str):
    """Dynamically load a class from a string like 'game_logic.game_logic.DeliriumLogic'"""
    module_path, class_name = registered_games.get(game_name, "").rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def parse_args():
    parser = argparse.ArgumentParser(description="Run the game engine.")
    parser.add_argument(
        "game_location",
        type=str,
        help="Location of the game (local or cloud).",
        default="local",
        nargs="?",
    )
    parser.add_argument(
        "game_name",
        type=str,
        help="What game we are running from the registered games.",
        default="delirium",
        nargs="?",
    )
    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()
    game_location = args.game_location
    game_name = args.game_name

    print(f"Game location: {game_location}")
    print(f"Game name: {game_name}")

    if game_name not in registered_games:
        print(f"Game '{game_name}' is not registered.")
        sys.exit(1)

    runner = get_runner(game_location)
    print(f"Using runner: {runner.__class__.__name__}")

    game_logic_cls = load_game_logic(game_name)
    game_logic = game_logic_cls()
    print(f"Loaded game logic: {game_logic_cls.__name__}")

    game_engine = GameEngine(game_logic, app_runner=runner, new_game=True)
    game_engine.play_game()
    print("Game engine started.")
