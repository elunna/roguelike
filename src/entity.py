import math
import tcod
from . import stages
from .config import RenderOrder


class Entity(object):
    """ A generic object to represent players, enemies, items, etc.
        We use a dictionary to manage the entity's Components.
    """

    def __init__(self, **kwargs):
        self.components = kwargs

    def __str__(self):
        if self.has_comp('name'):
            return self.name
        return 'Unnamed'

    def __getattr__(self, name):
        if name in self.components:
            return self.components[name]

        raise AttributeError('Entity has no component with attribute {}'.format(name))

    def __setattr__(self, key, value):
        if key == 'components':
            # self.components = value
            super().__setattr__('components', value)
        else:
            self.components[key] = value

    def __getstate__(self):
        """But if we try to pickle our d instance, we get RecursionError because
            of that __getattr__ which does the magic conversion of attribute
            access to key lookup. We can overcome that by providing the class
            with __getstate__ and __setstate__ methods.
            https://stackoverflow.com/questions/50156118/recursionerror-maximum-recursion-depth-exceeded-while-calling-a-python-object-w/50158865#50158865
        """
        return self.components

    def __setstate__(self, state):
        """See comment for __getstate__"""
        self.components = state

    def add_comp(self, **kwargs):
        for k, v in kwargs.items():
            self.components[k] = v

    def has_comp(self, component):
        if component in self.components:
            return True
        return False

    def rm_comp(self, component):
        if component in self.components:
            self.components.pop(component)
            return True
        return False

    def move(self, dx, dy):
        # Move the entity by a given amount
        dest_x = self.x + dx
        dest_y = self.y + dy

        if dest_x < 0 or dest_y < 0:
            raise ValueError('move cannot place entity in a negative x or y: ({}, {})'.format(dest_x, dest_y))
        self.x += dx
        self.y += dy

    def distance_to(self, other):
        return stages.Stage.distance_between_entities(self, other)
