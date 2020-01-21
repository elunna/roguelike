from abc import ABC, abstractmethod
import tcod
from . import config
from . import components
from .config import States


class Action(ABC):
    def __init__(self, consumes_turn=True):
        self.consumes_turn = consumes_turn

    @abstractmethod
    def perform(self, *args, **kwargs):
        pass


class ActionResult(object):
    def __init__(self, success=False, alt=None, new_state=None, msg=None):
        if success and alt:
            raise ValueError('ActionResult cannot have succeeded and provide an alternative Action!')

        self.success = success
        self.alt = alt
        self.new_state = new_state
        self.msg = msg


class WalkAction(Action):
    def __init__(self, dx, dy):
        super().__init__(consumes_turn=True)
        if abs(dx) > 1 or abs(dy) > 1:
            raise ValueError('WalkAction dx or dy cannot be < -1 or > 1.')
        self.dx = dx
        self.dy = dy

        # redraw_fov_on_success?

    def perform(self, *args, **kwargs):
        entity = kwargs['entity']
        stage = kwargs['stage']
        _game = kwargs['game']

        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        # Check for wall
        if stage.is_blocked(dest_x, dest_y):
            # There is a wall blocking our path
            return ActionResult(
                success=False,
                msg='You cannot walk into the wall...'
            )

        # Check for attacker
        target = stage.get_blocker_at_loc(dest_x, dest_y)

        if target:
            return ActionResult(alt=AttackAction(entity, self.dx, self.dy))

        # log.debug('Moving.')
        entity.move(self.dx, self.dy)

        # Need to redraw FOV
        _game.fov_recompute = True

        # Add walk into door
        # Add walk into water/lava/etc
        # Add walk over items

        return ActionResult(success=True)


class AttackAction(Action):
    def __init__(self, entity, dx, dy):
        if abs(dx) > 1 or abs(dy) > 1:
            raise ValueError('AttackAction dx or dy cannot be < -1 or > 1.')

        super().__init__()
        self.entity = entity
        self.dx = dx
        self.dy = dy

    def perform(self, *args, **kwargs):
        stage = kwargs['stage']
        dest_x = self.entity.x + self.dx
        dest_y = self.entity.y + self.dy

        if stage.is_blocked(dest_x, dest_y):
            return ActionResult(
                success=False,
                msg='You cannot attack the wall!'
            )

        target = stage.get_blocker_at_loc(dest_x, dest_y)

        if target:
            # Todo - refactor attack code here...
            attack_results = self.entity.fighter.attack(target)
            self.results.extend(attack_results)
            return ActionResult(success=True)

        return ActionResult(
            success=False,
            msg='There is nothing to attack at that position.'
        )



class WaitAction(Action):
    def perform(self, *args, **kwargs):
        return ActionResult(success=True)


class PickupAction(Action):
    def perform(self, *args, **kwargs):
        stage = kwargs['stage']
        entity = kwargs['entity']

        # todo: Move this functionality to stage....
        for e in stage.entities:
            item_pos_at_our_pos = e.x == entity.x and e.y == entity.y

            if e.has_comp('item') and item_pos_at_our_pos:
                # todo: Refactor add item into this.
                self.results.extend(entity.inv.add_item(e))

                # todo: Will probably break stuff....
                return ActionResult(success=True)

        return ActionResult(
            success=False,
            msg='There is nothing here to pick up.'
        )


class UseItemAction(Action):
    # todo: Let UseItemAction work on items NOT in an entity's inventory
    # todo: Use item on ground
    # todo: Use item that was thrown, etc.

    def __init__(self, inv_index, target_x=None, target_y=None):
        super().__init__()
        self.inv_index = inv_index
        self.target_x = target_x
        self.target_y = target_y

    def perform(self, *args, **kwargs):
        stage = kwargs['stage']
        fov_map = kwargs['fov_map']
        entity = kwargs['entity']
        item_entity = entity.inv.items[self.inv_index]
        item_comp = item_entity.item

        if item_comp.use_func is None:
            equippable_comp = item_entity.equippable if item_entity.has_comp('equippable') else None

            # If item is equippable, return an EquipAction
            if equippable_comp:
                return ActionResult(alt=EquipAction(entity, item_entity))

            # This item doesn't have a use function!
            return ActionResult(
                success=False,
                msg='The {} cannot be used.'.format(item_entity.name)
            )

        else:
            have_target = self.target_x and self.target_y

            # If the item requires a target, return a GetTargetAction
            if item_comp.targeting and not have_target:
                return ActionResult(alt=GetTargetAction(item_entity))

            # Use the item - was it consumed?
            item_use_results = entity.inv.use(
                item_entity,
                entities=stage.entities,
                fov_map=fov_map,
                target_x=self.target_x,
                target_y=self.target_y
            )

            # If the item was consumed - remove it from inventory.
            for result in item_use_results:
                if result.get('consumed'):
                    entity.inv.rm_item(item_entity)

                    return ActionResult(success=True)

            # Not consumed
            return ActionResult(success=False)


class EquipAction(Action):
    def __init__(self, e, item):
        super().__init__()
        self.e = e
        self.item = item

    def perform(self, *args, **kwargs):
        entity = kwargs['entity']
        if not self.item.has_comp('equippable'):
            return ActionResult(
                success=False,
                msg='You cannot equip the {}'.format(self.item.name)
            )
        else:
            equip_results = entity.equipment.toggle_equip(self.item)

            for equip_result in equip_results:
                equipped = equip_result.get('equipped')
                dequipped = equip_result.get('dequipped')

                if equipped:
                    return ActionResult(
                        success=True,
                        msg='You equipped the {}'.format(equipped.name)
                    )

                if dequipped:
                    return ActionResult(
                        success=True,
                        msg='You dequipped the {}'.format(dequipped.name)
                    )


# class UnequipAction():
    # def __init__(self, e, item):
        # pass


class DropItemAction(Action):
    def __init__(self, inv_index):
        super().__init__()
        self.inv_index = inv_index

    def perform(self, *args, **kwargs):
        entity = kwargs['entity']
        prev_state = kwargs['prev_state']

        item = entity.inv.items[self.inv_index]

        # todo: Refactor drop into this function
        # self.results.extend(entity.inv.drop(item))
        entity.inv.drop(item)


class StairUpAction(Action):
    def perform(self, *args, **kwargs):
        dungeon = kwargs['dungeon']
        entity = kwargs['entity']
        game = kwargs['game']

        stage = dungeon.get_stage()

        for entity in stage.entities:
            if entity.has_comp('stair_up'):
                hero_at_stairs = entity.x == entity.x and entity.y == entity.y
                if hero_at_stairs:

                    if dungeon.current_stage == 0:

                        return ActionResult(
                            success=False,
                            alt=LeaveGameAction(),
                            msg='You go up the stairs and leave the dungeon forever...',
                            new_state=States.HERO_DEAD
                        )

                    elif dungeon.move_upstairs():
                        stage = dungeon.get_stage()
                        game.redraw = True

                        return ActionResult(
                            success=True,
                            msg='You ascend the stairs up.'
                        )
                    else:
                        raise ValueError("Something weird happened with going upstairs!")

        return ActionResult(
            success=False,
            msg='There are no stairs here.'
        )


class StairDownAction(Action):
    def perform(self, *args, **kwargs):
        dungeon = kwargs['dungeon']
        entity = kwargs['entity']
        game = kwargs['game']
        stage = dungeon.get_stage()

        for entity in stage.entities:
            if entity.has_comp('stair_down'):
                hero_at_stairs = entity.x == entity.x and entity.y == entity.y

                if hero_at_stairs:
                    dungeon.mk_next_stage()

                    if dungeon.move_downstairs():
                        stage = dungeon.get_stage()
                        stage.populate()
                        game.redraw = True
                        return ActionResult(
                            success=True,
                            msg='You carefully descend the stairs down.',
                        )
                    else:
                        raise ValueError("Something weird happened with going downstairs!")

        return ActionResult(
            success=False,
            msg='There are no stairs here.'
        )


class LevelUpAction(Action):
    def __init__(self, stat):
        super().__init__(consumes_turn=False)
        valid_stats = ['hp', 'str', 'def']
        if stat in valid_stats:
            self.stat = stat
        else:
            raise ValueError('stat not valid! Must be one of: {}'.format(valid_stats))

    def perform(self, *args, **kwargs):
        entity = kwargs['entity']
        prev_state = kwargs['prev_state']

        if self.stat == 'hp':
            entity.fighter.base_max_hp += 20
            entity.fighter.hp += 20
            return ActionResult(success=True, msg='Boosted max HP!', new_state=States.HERO_TURN)


        elif self.stat == 'str':
            entity.fighter.base_power += 1
            return ActionResult(success=True, msg='Boosted strength!', new_state=States.HERO_TURN)

        elif self.stat == 'def':
            entity.fighter.base_defense += 1
            return ActionResult(success=True, msg='Boosted defense!', new_state=States.HERO_TURN)

        else:
            raise ValueError('invalid stat!')


class ExitAction(Action):
    def __init__(self, state):
        super().__init__(consumes_turn=False)
        self.state = state

    def perform(self, *args, **kwargs):
        prev_state = kwargs['prev_state']

        if self.state in (States.SHOW_INV, States.DROP_INV, States.SHOW_STATS):
            return ActionResult(success=True, new_state=prev_state)

        elif self.state == States.TARGETING:
            return ActionResult(
                success=True,
                new_state=prev_state,
                msg='Targeting cancelled.',
            )

        else:
            return ActionResult(success=True, new_state=States.MAIN_MENU)


class FullScreenAction(Action):
    def __init__(self):
        super().__init__(consumes_turn=False)

    def perform(self, *args, **kwargs):
        # Toggle fullscreen on/off
        tcod.console_set_fullscreen(fullscreen=not tcod.console_is_fullscreen())
        return ActionResult(success=True)


class GetTargetAction(Action):
    def __init__(self, item):
        super().__init__(consumes_turn=False)
        self.item = item

    def perform(self, *args, **kwargs):
        return ActionResult(
            success=True,
            new_state=States.TARGETING
        )


class TargetAction(Action):
    def __init__(self, x, y, lclick=None, rclick=None):
        if not lclick and not rclick:
            raise ValueError('TargetAction requires exactly 1 mouse button to be clicked.')
        elif lclick and rclick:
            raise ValueError('TargetAction requires exactly 1 mouse button to be clicked.')

        super().__init__(consumes_turn=False)
        self.x = x
        self.y = y
        self.lclick = lclick
        self.rclick = rclick

    def perform(self, *args, **kwargs):
        targeting_item = kwargs['targeting_item']
        state = kwargs['state']

        if self.lclick:
            # note: Due to the message console - we have to offset the y.
            self.y -= config.msg_height
            use_item_action = UseItemAction(targeting_item, target_x=self.x, target_y=self.y)
            return ActionResult(alt=use_item_action)

        elif self.rclick:
            return ActionResult(
                success=False,
                alt=ExitAction(state)
            )

class ShowInvAction(Action):
    def __init__(self, prev_state):
        super().__init__(consumes_turn=False)
        self.prev_state = prev_state

    def perform(self, *args, **kwargs):
        return ActionResult(
            success=True,
            new_state=States.SHOW_INV
        )

class DropInvAction(Action):
    def __init__(self, prev_state):
        super().__init__(consumes_turn=False)
        self.prev_state = prev_state

    def perform(self, *args, **kwargs):
        return ActionResult(
            success=True,
            new_state=States.DROP_INV
        )


class CharScreenAction(Action):
    def __init__(self, prev_state):
        super().__init__(consumes_turn=False)
        self.prev_state = prev_state

    def perform(self, *args, **kwargs):
        return ActionResult(
            success=True,
            new_state=States.SHOW_STATS
        )


class KillMonsterAction(Action):
    def __init__(self, entity):
        super().__init__(consumes_turn=False)
        if entity.has_comp('human'):
            raise ValueError('KillPlayerAction requires the entity to be a Monster!')

        self.entity = entity

    def perform(self, *args, **kwargs):
        self.entity.char = '%'
        self.entity.color = tcod.dark_red
        self.entity.blocks = False
        self.entity.render_order = config.RenderOrder.CORPSE
        self.entity.rm_comp('fighter')
        self.entity.rm_comp('ai')

        # Change to an item so we can pick it up!
        self.entity.item = components.Item(owner=self.entity)

        death_msg = 'The {} dies!'.format(self.entity.name.capitalize())
        self.entity.name = 'remains of ' + self.entity.name

        return ActionResult(
            success=True,
            msg=death_msg
        )


class KillPlayerAction(Action):
    def __init__(self, entity):
        super().__init__(consumes_turn=False)
        if not entity.has_comp('human'):
            raise ValueError('KillPlayerAction requires the entity to be a Player!')
        self.entity = entity

    def perform(self, *args, **kwargs):
        self.entity.char = '%'
        self.entity.color = tcod.dark_red

        return ActionResult(
            success=True,
            msg='You died!',
            new_state=States.HERO_DEAD
        )


class AddXPAction(Action):
    def __init__(self):
        super().__init__(consumes_turn=False)

    def perform(self, *args, **kwargs):
        pass


class LeaveGameAction():
    pass
