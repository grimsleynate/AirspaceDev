"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """

    def at_post_move(self, source_location, move_type="move", **kwargs):
        """Allow friendly NPCs to notice a character entering their room."""

        super().at_post_move(source_location, move_type=move_type, **kwargs)
        if not self.location or source_location == self.location:
            return

        source_area = source_location.db.map_area if source_location else None
        destination_area = self.location.db.map_area
        if source_area != destination_area:
            from world.mapping import send_map_sync

            send_map_sync(self)

        for occupant in self.location.contents:
            if occupant is not self and hasattr(occupant, "at_character_entered"):
                occupant.at_character_entered(self)

    def at_post_puppet(self, **kwargs):
        """Synchronize this character's server-owned map after selection."""

        super().at_post_puppet(**kwargs)
        from world.mapping import send_map_sync

        send_map_sync(self)

    def at_post_unpuppet(self, account=None, session=None, **kwargs):
        """Clear this character's map from a session returning to account menus."""

        super().at_post_unpuppet(account=account, session=session, **kwargs)
        if session:
            from world.mapping import MAP_PROTOCOL_REVISION

            session.msg(
                quasar_map_sync={
                    "revision": MAP_PROTOCOL_REVISION,
                    "character": {"id": self.id, "name": self.key},
                    "current": None,
                    "area": None,
                    "rooms": [],
                }
            )
