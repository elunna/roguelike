import random
import tcod
from . import config
from . import item_factory
from . import monster_factory
from . import stairs
from .entity import Entity
from .random_utils import from_dungeon_lvl
from .render_functions import RenderOrder
from .rect import Rect
from .tile import Tile


class Dungeon(object):
    def __init__(self, hero):
        self.hero = hero
        self.levels = []
        self.current_lvl = 0

        # Generate the first level on initialization
        self.generate_next_level()
        self.place_hero(self.current_lvl)
        self.current_map().populate()

    def current_map(self):
        return self.levels[self.current_lvl]

    def place_hero(self, level):
        x, y = self.levels[level].rooms[0].center()
        self.hero.x = x
        self.hero.y = y
        self.levels[level].entities.append(self.hero)

    def generate_next_level(self):
        # Generate next dungeon level
        # place up stair in the first room
        level_depth = len(self.levels) + 1
        new_map = Map(config.map_width, config.map_height, level_depth)
        new_map.make_map()
        self.levels.append(new_map)

    def move_downstairs(self):
        # Remove the hero from the current level
        if self.current_map().rm_hero():
            self.current_lvl += 1

            # Place the hero on the next level
            self.place_hero(self.current_lvl)

            return True
        return False

    def move_upstairs(self):
        if self.current_map().rm_hero():
            self.current_lvl -= 1

            # todo: Find where the up-stair is on the next level
            x, y = self.levels[self.current_lvl].rooms[-1].center()
            self.hero.x = x
            self.hero.y = y
            self.levels[self.current_lvl].entities.append(self.hero)
            return True
        return False

class Map(object):
    def __init__(self, width, height, dungeon_lvl=config.DEFAULT_DUNGEON_LVL):
        # Error checking
        if width < config.min_map_length or height < config.min_map_length:
            raise ValueError("The minimum map width/height is {}".format(config.min_map_length))
        elif dungeon_lvl <= 0:
            raise ValueError("The minimum map dungeon_lvl is 1")

        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.entities = []
        self.rooms = []
        self.dungeon_lvl = dungeon_lvl

    def rm_hero(self):
        for e in self.entities:
            if e.human:
                self.entities.remove(e)
                return True
        return False

    def find_down_stair(self):
        for e in self.entities:
            if e.stair_down:
                return e
        return None

    def initialize_tiles(self):
        return [[Tile(True) for y in range(self.height)] for x in range(self.width)]

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True
        return False

    def mk_room(self):
        # random width and height
        w = random.randint(config.room_min_len, config.room_max_len)
        h = random.randint(config.room_min_len, config.room_max_len)

        # Random position w/o going out of the map boundaries
        x = random.randint(0, self.width - w - 1)
        y = random.randint(0, self.height - h - 1)

        # Generate new Rect
        return Rect(x, y, w, h)

    def dig_room(self, rect):
        WALL_OFFSET = 1
        # Go through the tiles in the rectangle and make them passable.
        for x in range(rect.x1 + WALL_OFFSET, rect.x2 - WALL_OFFSET):

            for y in range(rect.y1 + WALL_OFFSET, rect.y2 - WALL_OFFSET):

                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def mk_tunnel_simple(self, room1, room2, horz_first=True):
        x1, y1 = room1.center()
        x2, y2 = room2.center()

        if horz_first:
            # First move horizontally, then vertically.
            self.dig_h_tunnel(x1, x2, y1)
            self.dig_v_tunnel(y1, y2, x2)
        else:
            # First move vertically, then horizontally
            self.dig_v_tunnel(y1, y2, x1)
            self.dig_h_tunnel(x1, x2, y2)

    def dig_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def dig_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def make_map(self):
        # Procedurally generate a dungeon map
        for _ in range(config.max_rooms):
            new_room = self.mk_room()

            # Double check the other rooms to make sure there are no intersections.
            for other_room in self.rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # There are no intersections, valid room.
                self.dig_room(new_room)

                # Get center coordinates
                (new_x, new_y) = new_room.center()

                last_room_centerx = new_x
                last_room_centery = new_y

                if self.rooms:
                    # For all rooms after the first: Connect with a tunnel.
                    last_room = self.rooms[-1]

                    # Flip a coin to decide vertical first or horizontal first
                    horz_first = bool(random.randint(0, 1))
                    self.mk_tunnel_simple(last_room, new_room, horz_first)
                else:
                    # Place stairs up in the first room
                    self.place_stairs_up(new_x, new_y)

                self.rooms.append(new_room)

        # Add the Stairs
        self.place_stairs_down(last_room_centerx, last_room_centery)

    def populate(self):
        """Populates the map with monsters and items.
            Possibly adds other entities: stairs/features/etc.
        """
        self.place_monsters()
        for room in self.rooms:
            self.place_items(room)

    def is_occupied(self, x, y):
        """Returns True if an entity is occupying the tile."""
        return any([entity for entity in self.entities if entity.x == x and entity.y == y])

    def get_random_non_wall_loc(self):
        """Find a random spot on the map that is not a Wall."""
        # Find all of the non-wall tiles
        valid_tiles = []
        for x in range(self.width):
            for y in range(self.height):
                if not self.tiles[x][y].blocked:
                    valid_tiles.append((x, y))

        # Return a random valid tile
        if valid_tiles:
            return random.choice(valid_tiles)
        return None

    def get_random_room_loc(self, room):
        """Find a random spot in a room."""
        x = random.randint(room.x1 + config.NW_OFFSET, room.x2 - config.SE_OFFSET)
        y = random.randint(room.y1 + config.NW_OFFSET, room.y2 - config.SE_OFFSET)
        return x, y

    def place_monsters(self):
        """Generates monsters for the map. For each monster, we pick a random
            non-wall and non-occupied spot on the map and places a random monster there.
        """
        # todo: Create a table for monster generation that increases difficulty
        # max_monsters_per_map = from_dungeon_lvl(config.max_monsters_weights, self.dungeon_lvl)

        monster_chances = monster_factory.monster_chances(self.dungeon_lvl)

        # Make sure there are value tiles
        if not self.get_random_non_wall_loc():
            return None

        for _ in range(config.max_monsters_per_map):
            x, y = self.get_random_non_wall_loc()

            if not self.is_occupied(x, y):
                monster = monster_factory.get_random_monster(x, y, monster_chances)
                self.entities.append(monster)

    def place_items(self, room):
        """Places a random set of items in a room. Items can be placed on top of
            other items to create a pile or even where other monsters are.
        """
        # max_items_per_room = from_dungeon_lvl(config.max_items_weights, self.dungeon_lvl)
        max_items_per_room = 5

        num_items = random.randint(0, max_items_per_room)
        item_chances = item_factory.item_chances(self.dungeon_lvl)

        for i in range(num_items):
            x, y = self.get_random_room_loc(room)

            if not self.is_occupied(x, y):
                item = item_factory.get_rnd_item(x, y, item_chances)
                self.entities.append(item)

    def place_stairs_down(self, x, y):
        if self.tiles[x][y].blocked:
            raise ValueError('Stairs cannot go on Wall tile!')

        stairs_comp = stairs.Stairs(floor=self.dungeon_lvl + 1)
        stair_up = Entity(
            x, y,
            '>',
            tcod.white,
            'Stairs Down',
            render_order=RenderOrder.STAIRS,
            stair_down=stairs_comp
        )
        self.entities.append(stair_up)
        return stair_up

    def place_stairs_up(self, x, y):
        if self.tiles[x][y].blocked:
            raise ValueError('Stairs cannot go on Wall tile!')

        stairs_comp = stairs.Stairs(floor=self.dungeon_lvl - 1)
        stair_up = Entity(
            x, y,
            '<',
            tcod.white,
            'Stairs Up',
            render_order=RenderOrder.STAIRS,
            stair_up=stairs_comp
        )
        self.entities.append(stair_up)
        return stair_up