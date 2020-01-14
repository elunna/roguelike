import tcod
from . import config
from .config import RenderOrder, EquipmentSlots
from .components import Fighter, ApproachingBehavior, Item, Equippable
from .entity import Entity
from .item_functions import heal, cast_confuse, cast_lightning, cast_fireball
from .random_utils import rnd_choice_from_dict, from_dungeon_lvl


# Update to take the level
item_chances = {
    'healing_potion': 35,
    # 'lightning_scroll': from_dungeon_lvl([[25, 4]], dungeon_lvl),
    # 'fireball_scroll': from_dungeon_lvl([[25, 6]], dungeon_lvl),
    # 'confusion_scroll': from_dungeon_lvl([[10, 2]], dungeon_lvl),
    'lightning_scroll': 5,
    'fireball_scroll': 5,
    'confusion_scroll': 5,
    'sword': 5,
    'shield': 5,
    # 'sword': from_dungeon_lvl([[5, 4]], dungeon_lvl),
    # 'shield': from_dungeon_lvl([[15, 8]], dungeon_lvl),
}

# Update to take the level
monster_chances = {
    'spider': 80,
    'orc': 80,
    'troll': 40,
    # 'troll': from_dungeon_lvl(config.troll_chances, dungeon_lvl)
}


def get_random_monster(x, y):
    monster_choice = rnd_choice_from_dict(monster_chances)
    return mk_entity(monster_choice, x, y)


def get_random_item(x, y):
    item_choice = rnd_choice_from_dict(item_chances)
    return mk_entity(item_choice, x, y)


def mk_entity(entity_name, x, y):
    if x < 0 or y < 0:
        raise ValueError('x and y coordinates must be 0 or greater!')

    if entity_name == 'spider':
        spider = Entity(
            x, y,
            's',
            tcod.desaturated_green,
            'Spider',
            blocks=True,
            render_order=RenderOrder.ACTOR,
        )
        spider.fighter = Fighter(owner=spider, hp=5, defense=0, power=2, xp=5)
        spider.ai = ApproachingBehavior(spider)
        return spider

    elif entity_name == 'orc':
        orc = Entity(
            x, y,
            'o',
            tcod.desaturated_green,
            'Orc',
            blocks=True,
            render_order=RenderOrder.ACTOR,
        )
        orc.fighter = Fighter(owner=orc, hp=10, defense=1, power=3, xp=35)
        orc.ai = ApproachingBehavior(orc)
        return orc

    elif entity_name == 'troll':
        troll = Entity(
            x, y,
            'T',
            tcod.darker_green,
            'Troll',
            blocks=True,
            render_order=RenderOrder.ACTOR,
        )
        troll.fighter = Fighter(owner=troll, hp=10, defense=2, power=4, xp=100)
        troll.ai = ApproachingBehavior(troll)
        return troll

    if entity_name == 'healing_potion':
        item = Entity(
            x, y,
            '!',
            tcod.violet,
            "Healing potion",
            render_order=RenderOrder.ITEM,
        )
        item.item = Item(item, use_func=heal, amt=40)
        return item

    elif entity_name == 'sword':
        item = Entity(
            x, y,
            '(',
            tcod.sky,
            'Sword',
        )
        item.item = Item(owner=item)
        item.equippable = Equippable(owner=item, slot=EquipmentSlots.MAIN_HAND, power_bonus=3)
        return item

    elif entity_name == 'dagger':
        item = Entity(
            0, 0,
            '(',
            tcod.sky,
            'Dagger',
        )
        item.item = Item(owner=item)
        item.equippable = Equippable(owner=item, slot=EquipmentSlots.MAIN_HAND, power_bonus=2)
        return item

    elif entity_name == 'shield':
        item = Entity(
            x, y,
            '[',
            tcod.darker_orange,
            'Shield',
        )
        item.item = Item(owner=item)
        item.equippable = Equippable(owner=item, slot=EquipmentSlots.OFF_HAND, defense_bonus=2)
        return item

    elif entity_name == 'ring of hp':
        item = Entity(
            x, y,
            '=',
            tcod.blue,
            'Ring of HP',
        )
        item.item = Item(owner=item)
        item.equippable = Equippable(owner=item, slot=EquipmentSlots.OFF_HAND, max_hp_bonus=50)
        return item

    elif entity_name == 'fireball_scroll':
        item = Entity(
            x, y,
            '?',
            tcod.yellow,
            "Fireball Scroll",
            render_order=RenderOrder.ITEM,
        )
        item.item = Item(
            owner=item,
            use_func=cast_fireball,
            targeting=True,
            targeting_msg='Left-click a target tile for the fireball, or right-click to cancel.',
            dmg=25,
            radius=3
        )
        return item

    elif entity_name == 'confusion_scroll':
        item = Entity(
            x, y,
            '?',
            tcod.yellow,
            "Confuse Scroll",
            render_order=RenderOrder.ITEM,
        )

        item.item = Item(
            owner=item,
            use_func=cast_confuse,
            targeting=True,
            targeting_msg='Left-click an enemy to confuse it, or right-click to cancel.',
        )
        return item

    elif entity_name == 'lightning_scroll':
        # Scroll of lightning bolt
        item = Entity(
            x, y,
            '?',
            tcod.yellow,
            "Lightning Scroll",
            render_order=RenderOrder.ITEM,
        )

        item.item = Item(
            owner=item,
            use_func=cast_lightning,
            dmg=40,
            max_range=5
        )
        return item

    raise ValueError('Unknown entity selected: {}'.format(entity_name))
