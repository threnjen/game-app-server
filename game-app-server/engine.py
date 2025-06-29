import argparse
import importlib
import sys
import json

from game_contracts.game_state import GameState
from game_contracts.runner_server_abc import RunnerServerABC


game_command_registries = {
    "delirium": "delirium_game_logic.command_registry.COMMAND_REGISTRY",
    "sample": "sample_game_logic.command_registry.COMMAND_REGISTRY",
}

registered_game_state = {
    "delirium": "delirium_game_logic.models.data_models.GameState",
    "sample": "sample_game_logic.models.data_models.GameState",
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
        self.game_id = game_id
        self.game_runner = self.load_runner_module(host_environment)
        initial_game_state = self.load_initial_game_state(game_id, game_name)
        command_registry = self.load_command_registry(game_name)
        self.game = self.load_game_state_model(game_name, initial_game_state)
        self.start_input_loop(command_registry)

    def load_runner_module(self, host_environment: str):
        if host_environment not in ["local", "cloud"]:
            print(f"Host environment '{host_environment}' is not supported.")
            sys.exit(1)

        runner = get_runner(host_environment)
        print(f"Loaded runner: {runner.__class__.__name__}")
        return runner

    def load_initial_game_state(self, game_id: str, game_name: str) -> dict:
        """Load the game state from a persistent storage."""
        # This is a placeholder for loading game state logic.
        # In a real application, you would retrieve the game state from a database or file.
        print(f"Loading game state for game_id: {game_id}, game_name: {game_name}")
        return {}

    def load_command_registry(self, game_name: str):
        registry_path = game_command_registries[game_name]
        module_path, attr_name = registry_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        command_registry = getattr(module, attr_name)
        return command_registry

    def load_game_state_model(
        self, game_name: str, initial_game_state: dict
    ) -> GameState:
        """Dynamically load a class from a string like 'delirium_game_logic.models.data_models.GameState"""
        registry_path = registered_game_state[game_name]
        module_path, attr_name = registry_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        game_state_model = getattr(module, attr_name)
        return game_state_model(**initial_game_state)

    def start_input_loop(self, command_registry: dict):

        while True:

            command_json = self.game_runner.poll_for_message_from_client(self.game_id)

            input_command_type = command_json.get("category")

            command_registry.get(input_command_type)(**command_json).execute(self.game)

            game_state = self.game.model_dump_json()

            self.game_runner.push_message_to_client(
                game_id=self.game_id, payload=json.loads(game_state)
            )

            self.save_game_state(game_state)

    def save_game_state(self, game_state: str):
        """Save the game state to a persistent storage."""
        # This is a placeholder for saving game state logic.
        # In a real application, you would save the game state to a database or file.
        print(f"Saving game state: {game_state}")


if __name__ == "__main__":

    args = parse_args()
    host_environment = args.host_environment
    game_name = args.game_name

    print(f"Game location: {host_environment}")
    print(f"Game name: {game_name}")
