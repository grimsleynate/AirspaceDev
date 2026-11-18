"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter
from evennia.contrib.rpg.traits import TraitHandler
from evennia.contrib.rpg.rpsystem import ContribRPCharacter
from evennia.utils import lazy_property

from .objects import ObjectParent
from .appearance import PLAYER_NAME, style


class Character(ObjectParent, ContribRPCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """

    inventory_capacity = 8

    @lazy_property
    def traits(self):
        """Core gauges such as Health."""

        return TraitHandler(self, db_attribute_key="character_traits")

    def inventory_items(self):
        """Return direct carried objects that occupy inventory slots."""

        return [
            item
            for item in self.contents
            if not bool(getattr(item, "is_equipped", False))
        ]

    def at_object_creation(self):
        """Create the server-owned progression and health state."""

        super().at_object_creation()
        from world.resources import ensure_character_resources
        from world.combat import ensure_character_progression

        ensure_character_progression(self)
        ensure_character_resources(self)

    def at_pre_object_receive(self, arriving_object, source_location, **kwargs):
        """Limit direct carried inventory; containers provide extra storage."""

        if (
            arriving_object not in self.contents
            and not bool(getattr(arriving_object, "is_equipped", False))
            and len(self.inventory_items()) >= self.inventory_capacity
        ):
            self.msg(
                f"Your direct inventory is full ({self.inventory_capacity} items). "
                "Put something in a container or drop an item first."
            )
            return False
        return super().at_pre_object_receive(arriving_object, source_location, **kwargs)

    def get_display_name(self, looker=None, **kwargs):
        """Render player characters distinctly from rooms and NPCs."""

        # ContribRPCharacter displays its generic short description here (for
        # example, "A normal person"). The room roster and clickable GUI
        # identify player characters by their actual character key instead.
        name = DefaultCharacter.get_display_name(self, looker, **kwargs)
        return style(name, PLAYER_NAME)

    def at_post_move(self, source_location, move_type="move", **kwargs):
        """Refresh client state and let room occupants react to an arrival."""

        super().at_post_move(source_location, move_type=move_type, **kwargs)
        if not self.location or source_location == self.location:
            return

        if self.db.combat_target_id:
            from world.combat import leave_combat

            leave_combat(self, message=True)

        source_area = source_location.db.map_area if source_location else None
        destination_area = self.location.db.map_area
        if source_area != destination_area:
            from world.mapping import send_map_sync

            send_map_sync(self)

        from world.audio import send_audio_scene
        from world.room_effects import send_room_effects

        send_audio_scene(self)
        send_room_effects(self)

        for occupant in self.location.contents:
            if occupant is not self and hasattr(occupant, "at_character_entered"):
                occupant.at_character_entered(self)

    def at_post_puppet(self, **kwargs):
        """Initialize and synchronize this character after selection."""

        from world.resources import ensure_character_resources

        ensure_character_resources(self)
        super().at_post_puppet(**kwargs)
        from world.accessibility import apply_accessibility_preferences
        from world.audio import send_audio_scene
        from world.room_effects import send_room_effects
        from world.mapping import send_map_sync
        from world.resources import send_character_resources

        send_map_sync(self)
        for session in self.sessions.all():
            apply_accessibility_preferences(self.account, session=session, character=self)
        send_audio_scene(self)
        send_room_effects(self)
        send_character_resources(self, force=True)

    def at_post_unpuppet(self, account=None, session=None, **kwargs):
        """Clear this character's client state for a session returning to account menus."""

        if self.db.combat_target_id:
            from world.combat import leave_combat

            leave_combat(self)
        super().at_post_unpuppet(account=account, session=session, **kwargs)
        if session:
            from world.audio import stop_audio
            from world.room_effects import clear_room_effects
            from world.mapping import MAP_PROTOCOL_REVISION
            from world.resources import clear_character_resources

            stop_audio(self, session=session, all=True, fade_ms=300)
            clear_room_effects(session)
            clear_character_resources(session)
            session.msg(
                benben_map_sync={
                    "revision": MAP_PROTOCOL_REVISION,
                    "character": {"id": self.id, "name": self.key},
                    "current": None,
                    "area": None,
                    "rooms": [],
                }
            )

    def apply_damage(self, amount, damage_type="damage", message=True):
        """Public hook for combat, hazards, and future abilities."""

        from world.resources import apply_damage

        return apply_damage(self, amount, damage_type=damage_type, message=message)

    def restore_health(self, amount=None):
        """Public hook for healing items and recovery systems."""

        from world.resources import restore_health

        return restore_health(self, amount=amount)

    def award_experience(self, amount, source=None):
        """Public hook for combat, quests, and future exploration rewards."""

        from world.combat import award_experience

        return award_experience(self, amount, source=source)
