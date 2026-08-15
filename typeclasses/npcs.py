"""Friendly non-player characters."""

from evennia.utils.evmenu import EvMenu

from .objects import Object


class FriendlyNPC(Object):
    """A stationary NPC that can greet characters and host dialogue."""

    dialogue_module = None

    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("get:false();puppet:false()")

    def at_character_entered(self, character):
        """Offer a short greeting once per visit without taking input focus."""

        character.msg(f"|c{self.key}|n notices your arrival and offers a welcoming nod.")

    def at_greet(self, character):
        character.location.msg_contents(
            f"$You() $conj(greet) {self.key}.", from_obj=character
        )
        character.msg(f'|c{self.key}|n says, "Welcome aboard. Talk to me when you are ready."')

    def at_talk(self, character, session=None):
        if not self.dialogue_module:
            character.msg(f"{self.key} has nothing to discuss right now.")
            return
        EvMenu(
            character,
            self.dialogue_module,
            startnode="node_start",
            session=session,
            npc=self,
        )


class OrientationGuide(FriendlyNPC):
    """The guide responsible for the tutorial's first objective."""

    dialogue_module = "world.tutorial_dialogue"

    def accept_tutorial_badge(self, character, badge):
        progress = dict(character.db.tutorial_progress or {})
        if progress.get("badge_returned"):
            character.msg(
                f'|c{self.key}|n says, "This badge is already registered. Keep it—you may need it."'
            )
            badge.move_to(character, quiet=True)
            return

        progress["badge_requested"] = True
        progress["badge_returned"] = True
        character.db.tutorial_progress = progress
        character.location.msg_contents(
            f"{self.key} scans the access badge and returns it to {character.key}.",
            exclude=character,
        )
        badge.move_to(character, quiet=True)
        character.msg(
            "|gOrientation objective complete.|n The guide points you toward the lift lobby. "
            "Explore both the operations deck above and engineering below; the departure route "
            "continues through engineering."
        )
