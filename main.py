from game_engine.engine import GameEngine
from game_logic.game_logic import DeliriumLogic

if __name__ == "__main__":

    game_logic = DeliriumLogic()
    game_engine = GameEngine(game_logic, new_game=True)
    game_engine.play_game()
