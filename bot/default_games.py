
from datetime import datetime

# Each key is a game name
# game_state can be any dict representing the initial state of the game
DEFAULT_GAMES = {
    "connect4": {
        "state" : [["⬜" for _ in range(6)] for _ in range(7)],
        "max_players" : 2

    }
    }