from enum import Enum
import tcod


class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3


def render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, msg_log, screen_width, screen_height, bar_width, panel_height, panel_y, colors):
    # Draw all the tiles in the game map

    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                # wall = game_map.tiles[x][y].block_sight
                # if wall:
                    # tcod.console_set_char_background(con, x, y, colors.get('dark_wall'), tcod.BKGND_SET)
                # else:
                    # tcod.console_set_char_background(con, x, y, colors.get('dark_ground'), tcod.BKGND_SET)

                visible = tcod.map_is_in_fov(fov_map, x, y)

                wall = game_map.tiles[x][y].block_sight

                if visible:
                    if wall:
                        tcod.console_set_char_background(con, x, y, colors.get('light_wall'), tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(con, x, y, colors.get('light_ground'), tcod.BKGND_SET)

                    game_map.tiles[x][y].explored = True        # It's visible therefore explored

                elif game_map.tiles[x][y].explored:
                    if wall:
                        tcod.console_set_char_background(con, x, y, colors.get('dark_wall'), tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(con, x, y, colors.get('dark_ground'), tcod.BKGND_SET)

	# Draw all entities in the list
    sorted_entities = sorted(entities, key=lambda x: x.render_order.value)

    for entity in sorted_entities:
        draw_entity(con, entity, fov_map)

    # Display console
    # tcod.console_set_default_foreground(con, tcod.white)
    # hp_display = 'HP: {0:02}/{1:02}'.format(player.fighter.hp, player.fighter.max_hp)

    # tcod.console_print_ex(
        # con,
        # 1,
        # screen_height - 2,
        # tcod.BKGND_NONE,
        # tcod.LEFT,
        # hp_display
    # )

    tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

    tcod.console_set_default_background(panel, tcod.black)
    tcod.console_clear(panel)

    # Print the game messages, one line at a time
    y = 1
    for msg in msg_log.messages:
        tcod.console_set_default_foreground(panel, msg.color)
        tcod.console_print_ex(panel, msg_log.x, y, tcod.BKGND_NONE, tcod.LEFT, msg.text)
        y += 1

    render_bar(
        panel,
        1, 1,
        bar_width,
        'HP',
        player.fighter.hp,
        player.fighter.max_hp,
        tcod.light_red,
        tcod.darker_red
    )

    tcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)


def clear_all(con, entities):
    # Clear all entities on the console
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity, fov_map):
    # Draw an entity on the console
    if tcod.map_is_in_fov(fov_map, entity.x, entity.y):
        tcod.console_set_default_foreground(con, entity.color)
        tcod.console_put_char(con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)



def clear_entity(con, entity):
    # Erase the character that represents this object
    tcod.console_put_char(con, entity.x, entity.y, ' ', tcod.BKGND_NONE)

def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    tcod.console_set_default_background(panel, back_color)
    tcod.console_rect(
        panel,
        x, y,
        total_width,
        1,
        False,
        tcod.BKGND_SCREEN
    )

    tcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        tcod.console_rect(
            panel,
            x, y,
            bar_width,
            1,
            False,
            tcod.BKGND_SCREEN
        )


    tcod.console_set_default_foreground(panel, tcod.white)

    tcod.console_print_ex(
        panel,
        int(x + total_width / 2),
        y,
        tcod.BKGND_NONE,
        tcod.CENTER,
        '{}: {}/{}'.format(name, value, maximum)
    )

