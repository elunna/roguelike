import tcod
from game_states import GameStates


def handle_keys(key, game_state):
    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn_keys(key)

    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)

    elif game_state == GameStates.INVENTORY:
        return handle_inv_keys(key)

    return {}


def handle_player_turn_keys(key):
    key_char = chr(key.c)

    # Actions
    if key_char == 'g' or key_char == ',':
        return {'pickup': True}
    elif key_char == 'i':
        return {'inventory': True}

    # Movement
    # Note: Add support for number pad movement
    if key.vk == tcod.KEY_UP or key_char == 'k':
        return {'move': (0, -1)}
    elif key.vk == tcod.KEY_DOWN or key_char == 'j':
        return {'move': (0, 1)}
    elif key.vk == tcod.KEY_LEFT or key_char == 'h':
        return {'move': (-1, 0)}
    elif key.vk == tcod.KEY_RIGHT or key_char == 'l':
        return {'move': (1, 0)}
    elif key_char == 'y':
        return {'move': (-1, -1)}
    elif key_char == 'u':
        return {'move': (1, -1)}
    elif key_char == 'b':
        return {'move': (-1, 1)}
    elif key_char == 'n':
        return {'move': (1, 1)}

    if key.vk == tcod.KEY_ENTER and key.lalt:
        # Alt+Enter: Toggle full screen
        return {'fullscreen': True}

    elif key.vk == tcod.KEY_ESCAPE:
        # Exit
        return {'exit': True}

    # No key was pressed
    return {}


def handle_player_dead_keys(key):
    key_char = chr(key.c)

    if key_char == 'i':
        return {'inventory': True}

    if key.vk == tcod.KEY_ENTER and key.lalt:
        # Alt+Enter: Toggle full screen
        return {'fullscreen': True}

    elif key.vk == tcod.KEY_ESCAPE:
        # Exit
        return {'exit': True}

    return {}


def handle_inv_keys(key):
    # Convert the key pressed to an index. a is 0, b is 1, etc.
    index = key.c - ord('a')

    if index >= 0:
        return {'inv_index': index}

    if key.vk == tcod.KEY_ENTER and key.lalt:
        # Alt+Enter: Toggle full screen
        return {'fullscreen': True}

    elif key.vk == tcod.KEY_ESCAPE:
        # Exit the menu
        return {'exit': True}

    return {}
