"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent
from .appearance import PLAYER_NAME, style


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """

    def at_object_creation(self):
        """Create the server-owned health and primary-resource state."""

        super().at_object_creation()
        from world.resources import ensure_character_resources
        from world.combat import ensure_character_progression

        ensure_character_progression(self)
        ensure_character_resources(self)

    def get_display_name(self, looker=None, **kwargs):
        """Render player characters distinctly from rooms and NPCs."""

        return style(super().get_display_name(looker, **kwargs), PLAYER_NAME)

    def access(self, accessing_obj, access_type="read", default=False, no_superuser_bypass=False, **kwargs):
        """Prevent responders sharing tutorial topology from perceiving each other."""

        if (
            access_type in {"view", "search"}
            and accessing_obj is not self
            and self.location
            and self.location == getattr(accessing_obj, "location", None)
            and bool(self.location.db.tutorial_shared)
        ):
            return False
        return super().access(
            accessing_obj,
            access_type=access_type,
            default=default,
            no_superuser_bypass=no_superuser_bypass,
            **kwargs,
        )

    def at_post_move(self, source_location, move_type="move", **kwargs):
        """Allow friendly NPCs to notice a character entering their room."""

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
        from world.resources import process_environment_transition

        send_audio_scene(self)
        process_environment_transition(self)

        for occupant in self.location.contents:
            owner_id = int(getattr(occupant.db, "tutorial_owner_id", 0) or 0)
            if (
                occupant is not self
                and (not owner_id or owner_id == self.id)
                and hasattr(occupant, "at_character_entered")
            ):
                occupant.at_character_entered(self)

        from world.tutorial import handle_room_entry

        handle_room_entry(self, source_location=source_location)
        from world.journal import send_journal_sync

        send_journal_sync(self)

    def at_post_puppet(self, **kwargs):
        """Initialize and synchronize this character after selection."""

        from world.resources import initialize_character

        initialize_character(self, include_starter_gear=True)
        from world.tutorial import ensure_tutorial_instance, is_legacy_tutorial_location

        if not self.db.tutorial_complete:
            ensure_tutorial_instance(
                self,
                enter=not self.location or is_legacy_tutorial_location(self.location),
            )
        super().at_post_puppet(**kwargs)
        from world.audio import send_audio_scene
        from world.mapping import send_map_sync
        from world.resources import send_character_resources
        from world.journal import send_journal_sync

        send_map_sync(self)
        send_journal_sync(self)
        send_audio_scene(self)
        send_character_resources(self, force=True)
        from world.tutorial import handle_room_entry

        handle_room_entry(self)

    def at_post_unpuppet(self, account=None, session=None, **kwargs):
        """Clear this character's map from a session returning to account menus."""

        if self.db.combat_target_id:
            from world.combat import leave_combat

            leave_combat(self)
        super().at_post_unpuppet(account=account, session=session, **kwargs)
        if session:
            from world.audio import stop_audio
            from world.mapping import MAP_PROTOCOL_REVISION
            from world.resources import clear_character_resources
            from world.journal import JOURNAL_PROTOCOL_REVISION

            stop_audio(self, session=session, all=True, fade_ms=300)
            clear_character_resources(session)
            session.msg(
                quasar_map_sync={
                    "revision": MAP_PROTOCOL_REVISION,
                    "character": {"id": self.id, "name": self.key},
                    "current": None,
                    "area": None,
                    "rooms": [],
                }
            )
            session.msg(
                quasar_journal_sync={
                    "revision": JOURNAL_PROTOCOL_REVISION,
                    "character": None,
                    "quests": [],
                    "tasks": [],
                }
            )

    def at_object_delete(self):
        """Delete the private tutorial story layer owned by this character."""

        from world.tutorial import delete_character_tutorial_instance

        delete_character_tutorial_instance(self)

        from typeclasses.items import (
            delete_character_starter_gear,
            delete_character_tutorial_items,
        )

        delete_character_tutorial_items(self)
        delete_character_starter_gear(self)
        return super().at_object_delete()

    def apply_damage(self, amount, damage_type="damage", message=True):
        """Public hook for combat, hazards, and future abilities."""

        from world.resources import apply_damage

        return apply_damage(self, amount, damage_type=damage_type, message=message)

    def restore_health(self, amount=None):
        """Public hook for medical items and recovery systems."""

        from world.resources import restore_health

        return restore_health(self, amount=amount)

    def award_experience(self, amount, source=None):
        """Public hook for combat, quests, and future exploration rewards."""

        from world.combat import award_experience

        return award_experience(self, amount, source=source)
