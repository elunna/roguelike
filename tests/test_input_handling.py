import pytest
import tcod
from pytest_mock import mocker
from ..src import actions
from ..src import input_handling
from ..src import config

States = config.States


def test_handle_keys__invalid_state__returns_NullAction():
    result = input_handling.handle_keys(key='a', state=None)
    # assert result == {}
    assert str(result) == 'NullAction'


def test_handle_keys__PLAYING__calls_handle_hero_turn_keys(mocker):
    mocker.patch.object(input_handling, 'handle_hero_turn_keys')
    input_handling.handle_keys(state=States.PLAYING, key='a')
    input_handling.handle_hero_turn_keys.assert_called()


def test_handle_keys__HERO_DEAD__calls_handle_hero_dead_keys(mocker):
    mocker.patch.object(input_handling, 'handle_hero_dead_keys')
    input_handling.handle_keys(state=States.HERO_DEAD, key='a')
    input_handling.handle_hero_dead_keys.assert_called()


def test_handle_keys__TARGETING__calls_handle_targeting_keys(mocker):
    mocker.patch.object(input_handling, 'handle_targeting_keys')
    input_handling.handle_keys(state=States.TARGETING, key='a')
    input_handling.handle_targeting_keys.assert_called()


def test_handle_keys__SHOW_INV__calls_handle_inv_keys(mocker):
    mocker.patch.object(input_handling, 'handle_inv_keys')
    input_handling.handle_keys(state=States.SHOW_INV, key='a')
    input_handling.handle_inv_keys.assert_called()


def test_handle_keys__DROP_INV__calls_handle_inv_keys(mocker):
    mocker.patch.object(input_handling, 'handle_inv_keys')
    input_handling.handle_keys(state=States.DROP_INV, key='a')
    input_handling.handle_inv_keys.assert_called()


def test_handle_keys__LEVEL_UP__calls_handle_lvl_up_menu(mocker):
    mocker.patch.object(input_handling, 'handle_lvl_up_menu')
    input_handling.handle_keys(state=States.LEVEL_UP, key='a')
    input_handling.handle_lvl_up_menu.assert_called()


def test_handle_keys__SHOW_STATS__calls_handle_char_scr(mocker):
    mocker.patch.object(input_handling, 'handle_char_scr')
    input_handling.handle_keys(state=States.SHOW_STATS, key='a')
    input_handling.handle_char_scr.assert_called()


""" Tests for handle_hero_turn_keys """


def test_handle_hero_turn_keys__stair_down():
    result = input_handling.handle_hero_turn_keys(state=None, key='>')
    assert isinstance(result, actions.StairDownAction)


def test_handle_hero_turn_keys__stair_up():
    result = input_handling.handle_hero_turn_keys(state=None, key='<')
    assert isinstance(result, actions.StairUpAction)


def test_handle_hero_turn_keys__pickup():
    result = input_handling.handle_hero_turn_keys(state=None, key=',')
    assert isinstance(result, actions.PickupAction)


def test_handle_hero_turn_keys__inventory():
    result = input_handling.handle_hero_turn_keys(state=None, key='i')
    assert isinstance(result, actions.ShowInvAction)


def test_handle_hero_turn_keys__drop_inventory():
    result = input_handling.handle_hero_turn_keys(state=None, key='d')
    assert isinstance(result, actions.DropInvAction)


def test_handle_hero_turn_keys__char_screen():
    result = input_handling.handle_hero_turn_keys(state=None, key='^x')
    assert isinstance(result, actions.CharScreenAction)


def test_handle_hero_turn_keys__wait():
    result = input_handling.handle_hero_turn_keys(state=None, key='.')
    assert isinstance(result, actions.WaitAction)


def test_handle_hero_turn_keys__move_N():
    result = input_handling.handle_hero_turn_keys(state=None, key='k')
    assert isinstance(result, actions.WalkAction)
    assert result.dx == 0
    assert result.dy == -1


def test_handle_hero_turn_keys__move_S():
    result = input_handling.handle_hero_turn_keys(state=None, key='j')
    assert isinstance(result, actions.WalkAction)
    assert result.dx == 0
    assert result.dy == 1


def test_handle_hero_turn_keys__move_E():
    result = input_handling.handle_hero_turn_keys(state=None, key='l')
    assert isinstance(result, actions.WalkAction)
    assert result.dx == 1
    assert result.dy == 0


def test_handle_hero_turn_keys__move_W():
    result = input_handling.handle_hero_turn_keys(state=None, key='h')
    assert isinstance(result, actions.WalkAction)
    assert result.dx == -1
    assert result.dy == 0


def test_handle_hero_turn_keys__move_NE():
    result = input_handling.handle_hero_turn_keys(state=None, key='u')
    assert isinstance(result, actions.WalkAction)
    assert result.dx == 1
    assert result.dy == -1


def test_handle_hero_turn_keys__move_NW():
    result = input_handling.handle_hero_turn_keys(state=None, key='y')
    assert isinstance(result, actions.WalkAction)
    assert result.dx == -1
    assert result.dy == -1


def test_handle_hero_turn_keys__move_SE():
    result = input_handling.handle_hero_turn_keys(state=None, key='n')
    assert isinstance(result, actions.WalkAction)
    assert result.dx == 1
    assert result.dy == 1


def test_handle_hero_turn_keys__move_SW():
    result = input_handling.handle_hero_turn_keys(state=None, key='b')
    assert isinstance(result, actions.WalkAction)
    assert result.dx == -1
    assert result.dy == 1


def test_handle_hero_turn_keys__fullscreen():
    result = input_handling.handle_hero_turn_keys(state=None, key='!a')
    assert isinstance(result, actions.FullScreenAction)


def test_handle_hero_turn_keys__escape():
    result = input_handling.handle_hero_turn_keys(state=None, key='esc')
    assert isinstance(result, actions.ExitAction)


def test_handle_hero_turn_keys__invalid_key__returns_NullAction():
    result = input_handling.handle_hero_turn_keys(state=None, key=None)
    assert str(result) == 'NullAction'


""" Tests for handle_hero_dead_keys """


def test_handle_hero_dead_keys__inventory():
    result = input_handling.handle_hero_dead_keys(state=None, key='i')
    assert isinstance(result, actions.ShowInvAction)


@pytest.mark.skip(reason='Fix Alt-Enter on tcod handling first')
def test_handle_hero_dead_keys__fullscreen():
    result = input_handling.handle_hero_dead_keys(state=None, key='!a')
    assert isinstance(result, actions.FullScreenAction)


def test_handle_hero_dead_keys__char_scr():
    result = input_handling.handle_hero_dead_keys(state=None, key='^x')
    assert isinstance(result, actions.CharScreenAction)


def test_handle_hero_dead_keys__esc():
    result = input_handling.handle_hero_dead_keys(state=None, key='esc')
    assert isinstance(result, actions.ExitAction)


def test_handle_hero_dead_keys__invalid_key__returns_NullAction():
    result = input_handling.handle_hero_dead_keys(state=None, key=None)
    assert str(result) == 'NullAction'


""" Tests for handle_inv_keys """


@pytest.mark.skip(reason='Fix Alt-Enter on tcod handling first')
def test_handle_inv_keys__fullscreen():
    result = input_handling.handle_inv_keys(state=None, key='alt-enter')
    assert isinstance(result, actions.FullScreenAction)


def test_handle_inv_keys__esc():
    result = input_handling.handle_inv_keys(state=None, key='esc')
    assert isinstance(result, actions.ExitAction)


def test_handle_inv_keys__SHOW_INV__uses_item():
    result = input_handling.handle_inv_keys(state=States.SHOW_INV, key='a')
    assert isinstance(result, actions.UseItemAction)
    assert result.inv_index == 0


def test_handle_inv_keys__DROP_INV__returns_DropItemAction():
    result = input_handling.handle_inv_keys(state=States.DROP_INV, key='a')
    assert isinstance(result, actions.DropItemAction)
    assert result.inv_index == 0


def test_handle_inv_keys__invalid_key__returns_NullAction():
    result = input_handling.handle_inv_keys(state=None, key='bla')
    assert str(result) == 'NullAction'


""" Tests for test_handle_main_menu(key) """


def test_handle_main_menu__new_game():
    result = input_handling.handle_main_menu(state=None, key='n')
    assert result == {'new_game': True}


def test_handle_main_menu__load_game():
    result = input_handling.handle_main_menu(state=None, key='c')
    assert result == {'load_game': True}


def test_handle_main_menu__options():
    result = input_handling.handle_main_menu(state=None, key='o')
    assert result == {'options': True}


def test_handle_main_menu__exit():
    result = input_handling.handle_main_menu(state=None, key='q')

    assert result == {'exit': True}
    # assert isinstance(result, actions.ExitAction)


@pytest.mark.skip(reason='look into later')
def test_handle_main_menu__esc__continues_game():
    result = input_handling.handle_main_menu(state=None, key='esc')

    assert result == {'exit': True}
    # assert isinstance(result, actions.ExitAction)


@pytest.mark.skip(reason='look into later')
def test_handle_main_menu__not_valid_key():
    result = input_handling.handle_main_menu(state=None, key=None)
    assert result == {}


""" Tests for test_handle_targeting_keys(key)"""


def test_handle_targeting_keys__esc__exits_targeting():
    result = input_handling.handle_targeting_keys(state=None, key='esc')
    assert isinstance(result, actions.ExitAction)


def test_handle_targeting_keys__non_valid__returns_NullAction():
    result = input_handling.handle_targeting_keys(state=None, key='z')
    assert str(result) == 'NullAction'


""" Tests for test_handle_lvl_up_menu(key)"""


def test_handle_lvl_up_menu__pick_constitution():
    result = input_handling.handle_lvl_up_menu(state=None, key='c')
    assert isinstance(result, actions.LevelUpAction)
    assert result.stat == 'hp'


def test_handle_lvl_up_menu__pick_strength():
    result = input_handling.handle_lvl_up_menu(state=None, key='s')
    assert isinstance(result, actions.LevelUpAction)
    assert result.stat == 'str'


def test_handle_lvl_up_menu__pick_defense():
    result = input_handling.handle_lvl_up_menu(state=None, key='d')
    assert isinstance(result, actions.LevelUpAction)
    assert result.stat == 'def'


def test_handle_lvl_up_menu__invalid_key__returns_NullAction():
    result = input_handling.handle_lvl_up_menu(state=None, key='z')
    assert str(result) == 'NullAction'


""" Tests for test_handle_char_scr(key):"""


def test_handle_char_scr__esc__returns_ExitAction():
    result = input_handling.handle_char_scr(state=None, key='esc')
    assert isinstance(result, actions.ExitAction)


def test_handle_char_scr__invalid_key__returns_NullAction():
    result = input_handling.handle_char_scr(state=None, key='z')
    assert str(result) == 'NullAction'


""" Tests for process_tcod_input"""


def test_process_tcod_input__a_returns_a():
    a_key = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('a'))
    assert  input_handling.process_tcod_input(a_key) == 'a'


def test_process_tcod_input__A_returns_A():
    A_key = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('A'))
    assert input_handling.process_tcod_input(A_key) == 'A'


def test_process_tcod_input__1_returns_1():
    one_key = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('1'))
    assert input_handling.process_tcod_input(one_key) == '1'


def test_process_tcod_input__control_x_returns_carrot_x():
    ctrl_x = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('x'), lctrl=True)
    assert input_handling.process_tcod_input(ctrl_x) == '^x'


def test_process_tcod_input__ESC_returns_esc():
    esc_key = tcod.Key(pressed=True, vk=tcod.KEY_ESCAPE, c=ord('\x1b'))
    assert input_handling.process_tcod_input(esc_key) == 'esc'


def test_process_tcod_input__comma_returns_comma():
    comma = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord(','))
    assert input_handling.process_tcod_input(comma) == ','


def test_process_tcod_input__dot_returns_dot():
    dot = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('.'))
    assert input_handling.process_tcod_input(dot) == '.'


def test_process_tcod_input_question():
    question = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('?'))
    assert input_handling.process_tcod_input(question) == '?'


def test_process_tcod_input_backslash():
    backslash = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('\\'))
    assert input_handling.process_tcod_input(backslash) == '\\'


def test_process_tcod_input_ranglebracket():
    rangle_bracket = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('>'))
    assert input_handling.process_tcod_input(rangle_bracket) == '>'


def test_process_tcod_input__shift_dot_returns_ranglebracket():
    shift_dot = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('.'), shift=True)
    assert input_handling.process_tcod_input(shift_dot) == '>'


def test_process_tcod_input_langlebracket():
    langle_bracket = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord('<'))
    assert input_handling.process_tcod_input(langle_bracket) == '<'


def test_process_tcod_input__shift_comma_returns_langlebracket():
    shift_comma = tcod.Key(pressed=True, vk=tcod.KEY_CHAR, c=ord(','), shift=True)
    assert input_handling.process_tcod_input(shift_comma) == '<'


def test_process_tcod_input__up_arrow_returns_k():
    up_arrow = tcod.Key(pressed=True, vk=tcod.KEY_UP)
    assert input_handling.process_tcod_input(up_arrow) == 'k'


def test_process_tcod_input__down_arrow_returns_j():
    down_arrow = tcod.Key(pressed=True, vk=tcod.KEY_DOWN)
    assert input_handling.process_tcod_input(down_arrow) == 'j'


def test_process_tcod_input__left_arrow_returns_h():
    left_arrow = tcod.Key(pressed=True, vk=tcod.KEY_LEFT)
    assert input_handling.process_tcod_input(left_arrow) == 'h'


def test_process_tcod_input__right_arrow_returns_l():
    right_arrow = tcod.Key(pressed=True, vk=tcod.KEY_RIGHT)
    assert input_handling.process_tcod_input(right_arrow) == 'l'


def test_process_tcod_input__numpad1__returns_b():
    numpad1 = tcod.Key(pressed=True, vk=tcod.KEY_KP1)
    assert input_handling.process_tcod_input(numpad1) == 'b'


def test_process_tcod_input__numpad2__returns_j():
    numpad2 = tcod.Key(pressed=True, vk=tcod.KEY_KP2)
    assert input_handling.process_tcod_input(numpad2) == 'j'


def test_process_tcod_input__numpad3__returns_n():
    numpad3 = tcod.Key(pressed=True, vk=tcod.KEY_KP3)
    assert input_handling.process_tcod_input(numpad3) == 'n'


def test_process_tcod_input__numpad4__returns_h():
    numpad4 = tcod.Key(pressed=True, vk=tcod.KEY_KP4)
    assert input_handling.process_tcod_input(numpad4) == 'h'


def test_process_tcod_input__numpad5__returns_dot():
    numpad5 = tcod.Key(pressed=True, vk=tcod.KEY_KP5)
    assert input_handling.process_tcod_input(numpad5) == '.'


def test_process_tcod_input__numpad6__returns_l():
    numpad6 = tcod.Key(pressed=True, vk=tcod.KEY_KP6)
    assert input_handling.process_tcod_input(numpad6) == 'l'


def test_process_tcod_input__numpad7__returns_y():
    numpad7 = tcod.Key(pressed=True, vk=tcod.KEY_KP7)
    assert input_handling.process_tcod_input(numpad7) == 'y'


def test_process_tcod_input__numpad8__returns_k():
    numpad8 = tcod.Key(pressed=True, vk=tcod.KEY_KP8)
    assert input_handling.process_tcod_input(numpad8) == 'k'


def test_process_tcod_input__numpad9__returns_u():
    numpad9 = tcod.Key(pressed=True, vk=tcod.KEY_KP9)
    assert input_handling.process_tcod_input(numpad9) == 'u'


""" Tests for test_handle_mouse()"""


def test_handle_mouse__NOT_TARGETING_returns_None():
    state = States.PLAYING
    rclick = tcod.Mouse(x=100, y=115, cx=11, cy=19, rbutton_pressed=True)
    result = input_handling.handle_mouse(state, rclick)
    assert result is None


def test_handle_mouse__TARGETING_rclick_returns_ExitAction():
    state = States.TARGETING
    rclick = tcod.Mouse(x=100, y=115, cx=11, cy=19, rbutton_pressed=True)
    result = input_handling.handle_mouse(state, rclick)

    # Test cx/cy because that is the cell the cursor is over in the console
    assert isinstance(result, actions.ExitAction)


def test_handle_mouse__TARGETING_lclick_returns_TargetAction():
    state = States.TARGETING
    mclick = tcod.Mouse(x=200, y=311, cx=16, cy=9, lbutton_pressed=True)
    result = input_handling.handle_mouse(state, mclick)

    # Test cx/cy because that is the cell the cursor is over in the console
    assert isinstance(result, actions.TargetAction)
    assert result.x == 16
    assert result.y == 9
    assert result.lclick


@pytest.mark.skip(reason='Middle button click not implemented yet.')
def test_handle_mouse__TARGETING_mclick_returns_TargetAction():
    state = States.TARGETING
    mclick = tcod.Mouse(x=50, y=22, cx=44, cy=2, lbutton_pressed=True)
    result = input_handling.handle_mouse(state, mclick)

    # Test cx/cy because that is the cell the cursor is over in the console
    assert isinstance(result, actions.TargetAction)
    assert result.x == 44
    assert result.y == 2
    assert result.mclick


""" Tests for key_to_index """


def test_key_to_index__a_equals_0():
    result = input_handling.key_to_index('a')
    assert result == 0


def test_key_to_index__z_equals_26():
    result = input_handling.key_to_index('z')
    assert result == 25


def test_key_to_index__A_equals_0():
    result = input_handling.key_to_index('A')
    assert result == -32


def test_key_to_index__Z_equals_26():
    result = input_handling.key_to_index('Z')
    assert result == -7


def test_key_to_index__invalid_key__returns_negative1():
    # with pytest.raises(ValueError):
        # input_handling.key_to_index('aa')

    result = input_handling.key_to_index('aa')
    assert result == -1
