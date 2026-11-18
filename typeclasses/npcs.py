"""Friendly and hostile non-player characters."""

from evennia.utils.evmenu import EvMenu

from .damageable import DamageableMixin
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
            character.msg(f"{self.get_display_name(character)} nods in return.")

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


class HostileNPC(DamageableMixin, Object):
    """A server-driven combatant with readable, interruptible attacks."""

    is_npc = True
    is_hostile = True

    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("get:false();puppet:false()")
        self.db.level = 1
        self.db.base_health_max = 55
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
        from world.health import ensure_health

        ensure_health(self)

    def get_display_name(self, looker=None, **kwargs):
        name = super().get_display_name(looker, **kwargs)
        if self.db.is_defeated:
            return style(f"fallen {name}", "|x")
        return style(name, HOSTILE_NPC_NAME)

    def get_display_desc(self, looker, **kwargs):
        description = super().get_display_desc(looker, **kwargs)
        if self.db.is_defeated:
            return f"{description}\nIt is motionless and no longer a threat."
        from world.health import health_of

        current, maximum = health_of(self)
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
