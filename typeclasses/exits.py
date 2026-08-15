"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

from evennia.objects.objects import DefaultExit

from .objects import ObjectParent


class Exit(ObjectParent, DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property and overrides some hooks
    and methods to represent the exits.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects child classes like this.

    """

    def is_visible_to_mapper(self, looker=None):
        """Return whether this exit is safe to reveal in player maps."""

        if self.db.map_hidden:
            return False
        return not looker or self.access(looker, "view")


class HiddenExit(Exit):
    """An exit command that works but is never advertised to a mapper.

    Use a descriptive command as the key, such as ``crawl north`` or
    ``crouch southwest``. Builders can later reveal it by setting
    ``exit.db.map_hidden = False`` and granting its ``view`` lock.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.map_hidden = True
        self.locks.add("view:false();traverse:all()")
