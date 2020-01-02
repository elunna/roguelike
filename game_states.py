from enum import Enum

class GameStates(Enum):
    # Note: In Python 3.6+, we can use "auto" feature to auto-increment
    PLAYERS_TURN = 1
    ENEMY_TURN = 2