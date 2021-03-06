from enum import Enum, auto
import tcod

class Slots(Enum):
    MAIN_HAND = 'main hand'
    OFF_HAND = 'off hand'

class RenderOrder(Enum):
    STAIRS = auto()
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()

class States(Enum):
    # Note: In Python 3.6+, we can use "auto" feature to auto-increment
    # Add a SETUP state for pre-game initialization?
    PLAYING = auto()
    HERO_DEAD = auto()       # X
    SHOW_INV = auto()
    DROP_INV = auto()
    TARGETING = auto()
    LEVEL_UP = auto()
    SHOW_STATS = auto()
    MAIN_MENU = auto()

    # Deprecated
    # ACTOR_TURN = auto()      # X
    # TURN_CONSUMED = auto()   # X

VERSION = 1.2
window_title = 'Infinity Dronez'
game_title = 'Infinity Dronez Version {}'.format(VERSION)
author = 'hackemslashem'


savefile = 'savegame.dat'
tileset_file = 'images/arial12x12.png'
menu_img = 'images/menu_bg.png'

scr_width = 80
scr_height = 50

# Console panels
bar_width = 20
panel_height = 7
panel_y = scr_height - panel_height
MAX_MENU_ITEMS = 26

msg_x = bar_width + 2
# msg_width = scr_width - bar_width - 2  # Same as scr_width
msg_height = 5

char_scr_width = 30
char_scr_height = 10

# Stage info
DEFAULT_DUNGEON_LVL = 1
stage_length_min = 3
stage_width = 60
stage_height = scr_height - panel_height - msg_height

# Room generation
room_max_len = 15
room_min_len = 3
NW_OFFSET = 1
SE_OFFSET = 2
max_rooms = 10
max_items_weights = [[1, 1], [2, 4]]

# Monster data
max_monsters_per_stage = 5
max_monsters_weights = [[2, 1], [3, 4], [5, 6]]
troll_chances = [[15, 3], [30, 5], [60, 7]]

# Level data
default_lvl = 1
starting_xp = 0
lvl_up_base = 200
lvl_up_factor = 150

# tcod.FOV_BASIC: Simple ray-cast implementation.
# tcod.FOV_DIAMOND
# tcod.FOV_SHADOW: Recursive shadow caster.
# tcod.FOV_PERMISSIVE(n): n starts at 0 (most restrictive) and goes up to 8 (most permissive.)
# tcod.FOV_RESTRICTIVE

fov_algorithm = 0              # 0 is default alg tcod uses
# fov_algorithm = tcod.FOV_BASIC

fov_light_walls = True          # Light up walls we see
fov_radius = 5                # How far can we see?

energy_per_turn = 100

colors = {
    # 'dark_wall': tcod.Color(0, 0, 100),
    # 'dark_ground': tcod.Color(50, 50, 150),
    'dark_wall': tcod.darker_gray,
    'dark_ground': tcod.darkest_gray,
    'light_wall': tcod.Color(130, 110, 50),
    'light_ground': tcod.Color(200, 180, 50)
}
