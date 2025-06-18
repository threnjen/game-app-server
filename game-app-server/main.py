from game_contracts.runner_server_abc import RunnerServerABC

# from game_contracts.game_logic_interface import GameLogicABC
import sys
import argparse
import importlib

registered_games = {
    "delirium": "delirium-game-logic.game_logic.DeliriumLogic",
    "sample": "sample-game_logic.sample_game.SampleGameLogic",
}


def get_runner(location: str) -> RunnerServerABC:
    if location == "local":
        from runners.local.runner_server import LocalRunnerServer

        return LocalRunnerServer()
    else:
        from runners.cloud.runner_server import CloudRunnerServer

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
    def __init__(self, host_environment, game_name, requesting_client) -> None:
        self.game_logic = self.load_game_module(game_name)
        self.game_runner = self.load_runner_module(host_environment)
        self.setup_game_state(requesting_client)
        self.requesting_client = requesting_client
        self.start_input_loop()

    def load_game_module(self, game_name):
        if game_name not in registered_games:
            print(f"Game '{game_name}' is not registered.")
            sys.exit(1)

        def load_game_logic(game_name: str):  # -> GameLogicABC:
            """Dynamically load a class from a string like 'game_logic.game_logic.DeliriumLogic'"""
            module_path, class_name = registered_games.get(game_name, "").rsplit(".", 1)
            module = importlib.import_module(module_path)
            return getattr(module, class_name)(requesting_client=self.requesting_client)

        game_logic = load_game_logic(game_name)

        return game_logic

    def load_runner_module(self, host_environment):
        if host_environment not in ["local", "cloud"]:
            print(f"Host environment '{host_environment}' is not supported.")
            sys.exit(1)

        runner = get_runner(host_environment)
        print(f"Loaded runner: {runner.__class__.__name__}")
        return runner

    def setup_game_state(self, requesting_client):
        game_state = self.game_logic.setup_game_state(requesting_client)
        self.game_runner.push_message_to_client(payload=game_state)

    def start_input_loop(self):
        while not self.game_logic.is_game_over():

            input_data = self.game_runner.poll_for_message_from_client()

            response = self.game_logic.handle_input(input_data)

            self.game_runner.push_message_to_client(payload=response)

        print("Game over. Exiting.")

    # game_engine = GameEngine(game_logic, app_runner=runner, new_game=True)
    # print("Game engine started.")


if __name__ == "__main__":

    args = parse_args()
    host_environment = args.host_environment
    game_name = args.game_name

    print(f"Game location: {host_environment}")
    print(f"Game name: {game_name}")
