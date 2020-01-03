import tcod
from game_messages import Message

class Inventory(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []


    def add_item(self, item):
        results = []

        if len(self.items) >= self.capacity:
            results.append({
                'item_added': None,
                'msg': Message('You cannot carry any more, your inventory is full.', tcod.yellow)
            })
        else:
            results.append({
                'item_added': item,
                'msg': Message('You pick up the {}!'.format(item.name), tcod.blue)
            })

            self.items.append(item)

        return results

    def use(self, item_entity, **kwargs):
        results = []
        item_comp = item_entity.item

        if item_comp.use_func is None:
            results.append({
                'msg': Message('The {} cannot be used.'.format(item_entity.name), tcod.yellow)
            })
        else:
            # How does this work? Is there a cleaner way to do this??
            # kwargs = {**item_comp.func_kwargs, **kwargs}  #

            kwargs.update(item_comp.func_kwargs)

            item_use_results = item_comp.use_func(self.owner, **kwargs)

            for result in item_use_results:
                if result.get('consumed'):
                    self.rm_item(item_entity)

            results.extend(item_use_results)

        return results

    def rm_item(self, item):
        self.items.remove(item)

    def drop(self, item):
        results = []
        item.x = self.owner.x
        item.y = self.owner.y

        self.rm_item(item)

        results.append({
            'item_dropped': item,
            'msg': Message('You dropped the {}.'.format(item.name), tcod.yellow)
        })

        return results
