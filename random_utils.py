from random import randint


def rnd_choice_index(chances):
    # Generate a random # up to the sum of all chance weights
    rnd_chance = randint(1, sum(chances))

    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        if rnd_chance <= running_sum:
            return choice
        choice += 1


def rnd_choice_from_dict(choice_dict):
    choices = list(choice_dict.keys())
    chances = list(choice_dict.values())

    return choices[rnd_choice_index(chances)]


def from_dungeon_lvl(table, dungeon_lvl):
    # Returns the weight appropriate for the dungeon lvl.
    for (value, lvl) in reversed(table):
        if dungeon_lvl >= lvl:
            return value

    return 0