"""Friendly non-player characters."""

from evennia.utils.evmenu import EvMenu

from .objects import Object
from .appearance import FRIENDLY_NPC_NAME, HOSTILE_NPC_NAME, style


class FriendlyNPC(Object):
    """A stationary NPC that can greet characters and host dialogue."""

    dialogue_module = None
    is_npc = True

    def get_display_name(self, looker=None, **kwargs):
        """Use green for friendly NPCs, distinct from cyan room titles."""

        return style(super().get_display_name(looker, **kwargs), FRIENDLY_NPC_NAME)

    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("get:false();puppet:false()")

    def at_character_entered(self, character):
        """Offer a short greeting once per visit without taking input focus."""

        character.msg(
            f"{self.get_display_name(character)} notices your arrival and offers a welcoming nod."
        )

    def at_greet(self, character, session=None, social="greet"):
        social = (
            social
            if social in {"greet", "nod", "wave", "smile", "bow", "salute"}
            else "greet"
        )
        phrase = {
            "greet": "$conj(greet)",
            "nod": "$conj(nod) to",
            "wave": "$conj(wave) to",
            "smile": "$conj(smile) at",
            "bow": "$conj(bow) to",
            "salute": "$conj(salute)",
        }[social]
        character.location.msg_contents(
            f"$You() {phrase} {self.key}.", from_obj=character
        )
        if self.dialogue_module:
            self.at_talk(character, session=session)
        else:
            character.msg(f'{self.get_display_name(character)} says, "Welcome aboard."')

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
                f'{self.get_display_name(character)} says, '
                '"This badge is already registered. Keep it—you may need it."'
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
        from world.audio import emit_audio

        emit_audio(character, "ui.objective_complete", priority=90)


class HostileNPC(Object):
    """A server-driven combatant with readable, interruptible attacks."""

    is_npc = True
    is_hostile = True

    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("get:false();puppet:false()")
        self.db.level = 1
        self.db.health_max = 55
        self.db.health_current = 55
        self.db.damage_min = 6
        self.db.damage_max = 9
        self.db.accuracy = 0
        self.db.evasion = 3
        self.db.armor = 2
        self.db.crit_chance = 0
        self.db.attack_name = "a lunging strike"
        self.db.telegraph_seconds = 2.0
        self.db.attack_interval = 3.0
        self.db.experience_reward = 35
        self.db.respawn_seconds = 20
        self.db.aggressive = False
        self.db.is_defeated = False
        self.db.combat_contributors = {}

    def get_display_name(self, looker=None, **kwargs):
        name = super().get_display_name(looker, **kwargs)
        if self.db.is_defeated:
            return style(f"fallen {name}", "|x")
        return style(name, HOSTILE_NPC_NAME)

    def get_display_desc(self, looker, **kwargs):
        description = super().get_display_desc(looker, **kwargs)
        if self.db.is_defeated:
            return f"{description}\nIt is motionless and no longer a threat."
        current = max(0, int(self.db.health_current or 0))
        maximum = max(1, int(self.db.health_max or 1))
        ratio = current / maximum
        condition = (
            "unhurt"
            if ratio >= 0.95
            else "damaged"
            if ratio >= 0.55
            else "badly wounded"
            if ratio >= 0.20
            else "barely standing"
        )
        return f"{description}\n|wCondition:|n {condition}."

    def at_character_entered(self, character):
        if self.db.aggressive and not self.db.is_defeated:
            character.msg(f"|h|r{self.key} turns toward you and prepares to attack.|n")
            from world.combat import engage

            engage(character, self)

    def reset_combatant(self, announce=False):
        from world.combat import reset_hostile

        reset_hostile(self, announce=announce)


class TrainingDrone(HostileNPC):
    """Low-risk baseline opponent used for the combat proving ground."""

    def at_object_creation(self):
        super().at_object_creation()
        self.db.health_max = 50
        self.db.health_current = 50
        self.db.damage_min = 5
        self.db.damage_max = 8
        self.db.attack_name = "a flashing shock baton"
        self.db.telegraph_seconds = 2.5
        self.db.experience_reward = 30
        self.db.desc = (
            "A waist-high security drone rolls on a magnetic ball, its shock baton folded "
            "along one side. A blue training beacon marks it as a controlled threat."
        )


class ScavengerParasite(HostileNPC):
    """Fast tutorial-grade organism feeding in abandoned compartments."""

    def at_object_creation(self):
        super().at_object_creation()
        self.db.health_max = 65
        self.db.health_current = 65
        self.db.damage_min = 7
        self.db.damage_max = 10
        self.db.evasion = 7
        self.db.armor = 1
        self.db.attack_name = "a coiled pounce"
        self.db.telegraph_seconds = 1.8
        self.db.attack_interval = 3.2
        self.db.experience_reward = 45
        self.db.desc = (
            "A pallid, many-jointed parasite clings close to the deck. Its feeding tendrils "
            "draw tight whenever movement crosses its milky eyes."
        )


class ArmoredScavenger(HostileNPC):
    """Slower armor-heavy comparison target for testing mitigation and skills."""

    def at_object_creation(self):
        super().at_object_creation()
        self.db.level = 2
        self.db.health_max = 90
        self.db.health_current = 90
        self.db.damage_min = 9
        self.db.damage_max = 13
        self.db.evasion = 1
        self.db.armor = 12
        self.db.attack_name = "a crushing forelimb sweep"
        self.db.telegraph_seconds = 3.0
        self.db.attack_interval = 4.0
        self.db.experience_reward = 70
        self.db.desc = (
            "A mature scavenger drags a carapace thickened with fused insulation and metal "
            "scrap. One swollen forelimb rises whenever it senses a nearby pulse."
        )
