import argparse
import importlib
import sys

from game_contracts.game_logic_interface import GameLogicABC
from game_contracts.runner_server_abc import RunnerServerABC

registered_games = {
    "delirium": "delirium-game-logic.game_logic.DeliriumLogic",
    "sample": "sample-game_logic.sample_game.SampleGameLogic",
}


def get_runner(location: str) -> RunnerServerABC:
    if location == "local":
        from runners.local.server_runner import LocalRunnerServer

        return LocalRunnerServer()
    else:
        from runners.cloud.server_runner import CloudRunnerServer

        return CloudRunnerServer()


def parse_args():
    parser = argparse.ArgumentParser(description="Set up the game details.")
    parser.add_argument(
        "host_environment",
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


class GameAppServer:
    def __init__(self, host_environment, game_name, game_id) -> None:
        self.game_runner = self.load_runner_module(host_environment)
        game_state = self.load_game_state(game_id, game_name)
        self.game_logic = self.load_game_module(game_state, game_name)
        self.initialize_game_state(game_state)
        self.start_input_loop()

    def load_runner_module(self, host_environment: str):
        if host_environment not in ["local", "cloud"]:
            print(f"Host environment '{host_environment}' is not supported.")
            sys.exit(1)

        runner = get_runner(host_environment)
        print(f"Loaded runner: {runner.__class__.__name__}")
        return runner

    def load_game_state(self, game_id: str, game_name: str) -> dict:
        """Load the game state from a persistent storage."""
        # This is a placeholder for loading game state logic.
        # In a real application, you would retrieve the game state from a database or file.
        print(f"Loading game state for game_id: {game_id}, game_name: {game_name}")
        return {}

    def load_game_module(self, game_state: dict, game_name: str) -> GameLogicABC:
        """Dynamically load a class from a string like 'game_logic.game_logic.DeliriumLogic'"""
        if game_name not in registered_games:
            print(f"Game '{game_name}' is not registered.")
            sys.exit(1)

        module_path, class_name = registered_games.get(game_name, "").rsplit(".", 1)
        module = importlib.import_module(module_path)

        game_logic = getattr(module, class_name)(game_state)

        return game_logic

    def initialize_game_state(self, game_state: dict):
        game_state = self.game_logic.get_game_state()
        self.game_runner.push_message_to_client(payload=game_state)

    def save_game_state(self, game_state: dict):
        """Save the game state to a persistent storage."""
        # This is a placeholder for saving game state logic.
        # In a real application, you would save the game state to a database or file.
        print(f"Saving game state: {game_state}")

    def start_input_loop(self):

        while not self.game_logic.is_game_over():

            input_data = self.game_runner.poll_for_message_from_client()

            response = self.game_logic.parse_client_message(input_data)

            self.save_game_state(self.game_logic.get_game_state())

            self.game_runner.push_message_to_client(payload=response)

        print("Game over. Exiting.")


if __name__ == "__main__":

    args = parse_args()
    host_environment = args.host_environment
    game_name = args.game_name

    print(f"Game location: {host_environment}")
    print(f"Game name: {game_name}")
