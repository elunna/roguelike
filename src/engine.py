import tcod
from . import config
from . import game
from . import logger
from . import render_functions
from .config import States
from .data_loaders import load_game, save_game
from .death_functions import kill_monster, kill_hero
from .fov import initialize_fov, recompute_fov
from .input_handling import handle_keys, handle_mouse, handle_main_menu, process_tcod_input

log = logger.setup_logger()


def main():
    log.debug('Started new game.')

    render_eng = render_functions.RenderEngine()
    show_main_menu = True
    show_load_err_msg = False
    main_menu_bg_img = tcod.image_load(filename=config.menu_img)
    key = tcod.Key()
    mouse = tcod.Mouse()

    while True:
        # todo: This runs all the time! Make it wait...

        # Deprecated since version 9.3: Use the tcod.event.get function to check for events.
        tcod.sys_check_for_event(
            mask=tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE,
            k=key,
            m=mouse
        )

        # When I can re-arrange input after rendering - re-enable this...
        # tcod.sys_wait_for_event(
            # mask=tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE,
            # k=key,
            # m=mouse,
            # flush=True
        # )

        if show_main_menu:
            render_eng.render_main_menu(main_menu_bg_img)

            if show_load_err_msg:
                render_eng.render_msg_box(render_eng, 'No save game to load', 50)

            # Update the display to represent the root consoles current state.
            tcod.console_flush()

            key_char = process_tcod_input(key)
            action = handle_main_menu(state=None, key=key_char)

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game = action.get('exit')
            options = action.get('options')

            if show_load_err_msg and (new_game or load_saved_game or exit_game):
                show_load_err_msg = False
            elif new_game:
                log.debug('New game selected.')
                _game = game.Game()

                show_main_menu = False

            elif load_saved_game:
                log.debug('Load game selected.')
                try:
                    _game = load_game(config.savefile)

                    show_main_menu = False
                except FileNotFoundError:
                    show_load_err_msg = True

            elif options:
                # todo: Fill out options menu
                log.debug('Options selected - STUB!')

            elif exit_game:
                log.debug('Exit selected')
                break
        else:
            # Reset a console to its default colors and the space character.
            render_eng.con.clear()

            play_game(_game, render_eng)
            show_main_menu = True


def play_game(g, render_eng):
    log.debug('Calling play_game...')

    key = tcod.Key()
    mouse = tcod.Mouse()

    # Deprecated since version 9.3: Use the tcod.event module to check for "QUIT" type events.
    # while not tcod.console_is_window_closed():

    log.debug('Entering game loop...')
    # Game loop
    while True:
        if g.redraw:
            # Reset the stage
            g.stage = g.dungeon.get_stage()

            g.fov_map = initialize_fov(g.stage)
            g.fov_recompute = True
            render_eng.con.clear()
            # libtcod.console_clear(con)
            g.redraw = False


        if g.fov_recompute:
            log.debug('fov_recompute...')
            recompute_fov(
                g.fov_map,
                g.hero.x,
                g.hero.y,
                config.fov_radius,
                config.fov_light_walls,
                config.fov_algorithm
            )

        # Render all entities
        render_eng.render_all(
            g.dungeon,
            g.fov_map,
            g.fov_recompute,
            g.msg_log,
            mouse,
            g.state,
            g.turns
        )

        g.fov_recompute = False       # Mandatory

        # Presents everything on screen
        tcod.console_flush()

        # Clear all entities
        render_eng.clear_all(g.stage.entities)

        # Capture new user input
        # Deprecated since version 9.3: Use the tcod.event.get function to check for events.
        # tcod.sys_check_for_event(
            # mask=tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE,
            # k=key,
            # m=mouse
        # )

        # Flush False - returns 2 key events
        # tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('h'))
        # tcod.Key(pressed=True, vk=tcod.KEY_TEXT, text='h')

        # Flush True: returns just this
        # tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('h'))

        if not g.action_queue.empty():
            action = g.action_queue.get()

        else:
            # Nothing is waiting in the action queue - collect more actions
            tcod.sys_wait_for_event(
                mask=tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE,
                k=key,
                m=mouse,
                flush=True
            )

            # Get keyboard/mouse input
            key_char = process_tcod_input(key)

            action = handle_keys(g.state, key_char)
            mouse_action = handle_mouse(g.state, mouse)

            if mouse_action:
                # Mouse action will take priority over keys (for now)
                log.debug('mouse_action: {}'.format(mouse_action))
                action = mouse_action

        if action:
            # Go with keyboard action
            action_result = process_action(action, g.hero, g)

            # Print any messges
            # If failed - don't consume turn
            # If succeed - consume turn if required
            # If new state - change the state
            # If alternate - Add the new Action to the queue

        if g.state == States.MAIN_MENU:
            g.redraw = True
            g.state = States.HERO_TURN
            save_game(config.savefile, g)
            return

        # if mouse_action?

        if g.state == States.WORLD_TURN:
            log.debug('Turn: {}'.format(g.turns))

            # Increment turn counter
            # This *may* go elsewhere, but we'll try it here first.
            g.turns += 1

            for entity in g.stage.entities:

                if entity.has_comp('ai'):
                    turn_results = entity.ai.take_turn(
                        g.hero,
                        g.fov_map,
                        g.stage,
                    )

                    for result in turn_results:
                        msg = result.get('msg')
                        dead_entity = result.get('dead')

                        if msg:
                            g.msg_log.add(msg)

                        if dead_entity:
                            if dead_entity == g.hero:
                                msg, g.state = kill_hero(dead_entity)
                            else:
                                msg = kill_monster(dead_entity)

                            g.msg_log.add(msg)

                            if g.state == States.HERO_DEAD:
                                break

                    if g.state == States.HERO_DEAD:
                        break

            else:
                g.state = States.HERO_TURN

        # check_for_quit()


def process_action(action, entity, g):
    log.debug('process_action: {} - State: {}'.format(action, g.state))
    hero_turn_results = []

    action.perform(
        state=g.state,
        prev_state=g.prev_state,
        dungeon=g.dungeon,
        stage=g.stage,
        fov_map=g.fov_map,
        entity=entity,
        targeting_item=g.targeting_item,
        game=g,
    )

    hero_turn_results = action.results

    # Increment turn if necessary
    if action.consumes_turn:
        g.state = States.WORLD_TURN

    for result in hero_turn_results:
        alternate = result.get('alternate')
        new_state = result.get('state')
        fov_recompute = result.get('fov_recompute')
        redraw = result.get('redraw')
        msg = result.get('msg')
        dead_entity = result.get('dead')
        item_added = result.get('item_added')
        item_dropped = result.get('item_dropped')
        equip = result.get('equip')
        targeting = result.get('targeting')

        xp = result.get('xp')

        if new_state:
            g.state = new_state

        if alternate:
            g.action_queue.put(alternate)

        if fov_recompute:
            g.fov_recompute = True

        if redraw:
            g.redraw = True

        if msg:
            log.debug('msg: {}.'.format(msg))
            g.msg_log.add(msg)

        if xp:
            log.debug('Adding xp.')
            leveled_up = g.hero.lvl.add_xp(xp)

            if leveled_up:
                log.debug('Hero level up.')
                g.msg_log.add('Your battle skills grow stronger! You reached level {}!'.format(g.hero.lvl.current_lvl))
                g.prev_state = g.state  # Should be WORLD_TURN
                g.state = States.LEVEL_UP

        if dead_entity:
            log.debug('Dead entity.')
            if dead_entity == g.hero:
                msg, state = kill_hero(dead_entity)
                # Add KillPlayerAction here....
            else:
                msg = kill_monster(dead_entity)
                # Add KillMonsterAction here....

            g.msg_log.add(msg)

        if item_added:
            log.debug('Item added.')
            g.stage.entities.remove(item_added)
            g.state = States.WORLD_TURN

        if targeting:
            log.debug('Targeting.')
            # Set to HERO_TURN so that if cancelled, we don't go back to inv.
            g.prev_state = States.HERO_TURN
            g.state = States.TARGETING

            g.targeting_item = targeting
            g.msg_log.add(g.targeting_item.item.targeting_msg)

        if item_dropped:
            log.debug('Item dropped.')
            g.stage.entities.append(item_dropped)
            g.state = States.WORLD_TURN

        if equip:
            log.debug('Equip.')
            equip_results = g.hero.equipment.toggle_equip(equip)

            for equip_result in equip_results:
                equipped = equip_result.get('equipped')
                dequipped = equip_result.get('dequipped')

                if equipped:
                    g.msg_log.add('You equipped the {}'.format(equipped.name))

                if dequipped:
                    g.msg_log.add('You dequipped the {}'.format(dequipped.name))

            g.state = States.WORLD_TURN


def check_for_quit():
    # AttributeError: module 'tcod' has no attribute 'event'
    for event in tcod.event.get():
        if event.type == "QUIT":
            raise SystemExit()
