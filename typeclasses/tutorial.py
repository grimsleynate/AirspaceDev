"""Private rooms, exits, people, creatures, and items for Quasar's tutorial."""

from typeclasses.exits import Exit
from typeclasses.items import EquipableItem, PortableItem
from typeclasses.npcs import FriendlyNPC, HostileNPC
from typeclasses.objects import InspectableScenery, PuzzleClue
from typeclasses.rooms import Room


def _owner_lock(owner_id):
    return f"id({int(owner_id)}) or perm(Admin)"


def _set_lock_types(obj, lockstring):
    """Replace selected lock types in one save without duplicate-lock warnings."""

    current = {}
    for lockdef in str(obj.locks).split(";"):
        if ":" in lockdef:
            access_type, _rhs = lockdef.split(":", 1)
            current[access_type.strip()] = lockdef.strip()
    for lockdef in lockstring.split(";"):
        if ":" in lockdef:
            access_type, _rhs = lockdef.split(":", 1)
            current[access_type.strip()] = lockdef.strip()
    obj.locks.replace(";".join(current.values()))


class TutorialOwnedMixin:
    """Ownership metadata and locks for character-private tutorial content."""

    def assign_tutorial_owner(self, character, instance_id, role):
        owner_id = int(character.id)
        self.db.tutorial_owner_id = owner_id
        self.db.tutorial_instance_id = str(instance_id)
        self.db.tutorial_role = str(role)
        self.tags.add(str(instance_id), category="quasar_tutorial_instance")
        self.tags.add(str(owner_id), category="quasar_tutorial_owner")


class TutorialRoom(TutorialOwnedMixin, Room):
    """A shared tutorial room whose story layer remains character-private."""

    def assign_tutorial_owner(self, character, instance_id, role):
        super().assign_tutorial_owner(character, instance_id, role)
        allowed = _owner_lock(character.id)
        _set_lock_types(self, f"view:{allowed};search:{allowed};get:false()")

    def at_pre_object_receive(self, arriving_object, source_location, **kwargs):
        return super().at_pre_object_receive(arriving_object, source_location, **kwargs)

    def atmosphere_for(self, character=None):
        """Return this room's per-character pressure state."""

        if not character:
            return str(self.db.atmosphere or "vacuum")
        state = dict(character.db.tutorial_progress or {})
        role = str(self.db.tutorial_role or "")
        if role == "command_center":
            return "vacuum" if state.get("command_decompressed") else "breathable"
        if role == "command_pressure_lock":
            if state.get("command_decompressed"):
                return "vacuum"
            return str(state.get("pressure_lock_atmosphere", "vacuum"))
        return str(self.db.atmosphere or "vacuum")

    def get_display_characters(self, looker, **kwargs):
        """Tutorial responders share topology but are invisible to one another."""

        return ""

    def msg_contents(self, text=None, exclude=None, from_obj=None, mapping=None, **kwargs):
        """Keep actor-originated room messages inside one character's story layer."""

        from evennia.utils.utils import make_iter

        def _is_character(obj):
            return bool(
                getattr(obj, "is_typeclass", None)
                and obj.is_typeclass(
                    "evennia.objects.objects.DefaultCharacter", exact=False
                )
            )

        mapping = mapping or {}
        candidates = [from_obj, *mapping.values(), *make_iter(exclude)]
        audience_id = None
        for candidate in candidates:
            if not candidate:
                continue
            db = getattr(candidate, "db", None)
            owner_id = int(getattr(db, "tutorial_owner_id", 0) or 0)
            if owner_id:
                audience_id = owner_id
                break
            if _is_character(candidate):
                audience_id = candidate.id
                break
        hidden = []
        if audience_id:
            hidden = [
                obj
                for obj in self.contents
                if _is_character(obj) and obj.id != audience_id
            ]
        combined_exclude = list(make_iter(exclude)) + hidden
        return super().msg_contents(
            text=text,
            exclude=combined_exclude,
            from_obj=from_obj,
            mapping=mapping,
            **kwargs,
        )

    def get_display_desc(self, looker, **kwargs):
        from world.tutorial import room_description

        return room_description(self, looker)

    def get_display_footer(self, looker, **kwargs):
        footer = super().get_display_footer(looker, **kwargs)
        if not looker:
            return footer
        from world.tutorial import objective_hint

        hint = objective_hint(looker, room=self)
        return "\n".join(part for part in (footer, hint) if part)

    def get_room_info(self, looker=None):
        payload = super().get_room_info(looker)
        atmosphere = self.atmosphere_for(looker)
        payload["atmosphere"] = atmosphere
        payload["terrain"] = "interior" if atmosphere == "breathable" else "vacuum"
        return payload


class TutorialExit(TutorialOwnedMixin, Exit):
    """Owner-only movement with combat and pressure-lock behavior."""

    def assign_tutorial_owner(self, character, instance_id, role):
        super().assign_tutorial_owner(character, instance_id, role)
        allowed = _owner_lock(character.id)
        _set_lock_types(self, f"view:{allowed};traverse:{allowed}")

    def at_traverse(self, traversing_object, target_location, **kwargs):
        owner_id = int(self.db.tutorial_owner_id or 0)
        if owner_id and traversing_object.id != owner_id and not traversing_object.check_permstring("Admin"):
            traversing_object.msg("That route belongs to another distress response.")
            return

        active = [
            obj
            for obj in self.location.contents
            if getattr(obj, "is_hostile", False)
            and int(obj.db.tutorial_owner_id or 0) == traversing_object.id
            and not obj.db.is_defeated
        ]
        fleeing_juno = (
            self.location.db.tutorial_role == "command_center"
            and target_location.db.tutorial_role == "command_pressure_lock"
        )
        if active and not fleeing_juno:
            traversing_object.msg(f"|r{active[0].key} blocks your escape. Deal with the threat first.|n")
            return

        lock_room = None
        if self.location.db.tutorial_role == "command_pressure_lock":
            lock_room = self.location
        elif target_location.db.tutorial_role == "command_pressure_lock":
            lock_room = target_location
        if lock_room:
            from world.tutorial import cycle_airlock_for_exit

            if not cycle_airlock_for_exit(
                traversing_object, lock_room, self.location, target_location
            ):
                return
        return super().at_traverse(traversing_object, target_location, **kwargs)


class TutorialDetail(TutorialOwnedMixin, InspectableScenery):
    """Character-private visible evidence inside a shared tutorial room."""

    def assign_tutorial_owner(self, character, instance_id, role):
        super().assign_tutorial_owner(character, instance_id, role)
        allowed = _owner_lock(character.id)
        _set_lock_types(self, f"view:{allowed};search:{allowed};get:false();drop:false();give:false()")


class TutorialClue(TutorialOwnedMixin, PuzzleClue):
    """Private evidence whose final line explicitly communicates a clue."""

    def assign_tutorial_owner(self, character, instance_id, role):
        super().assign_tutorial_owner(character, instance_id, role)
        allowed = _owner_lock(character.id)
        _set_lock_types(self, f"view:{allowed};search:{allowed};get:false();drop:false();give:false()")


class TutorialQuestItem(TutorialOwnedMixin, PortableItem):
    """Character-private tutorial item that cannot be discarded mid-scenario."""

    def assign_tutorial_owner(self, character, instance_id, role):
        super().assign_tutorial_owner(character, instance_id, role)
        allowed = _owner_lock(character.id)
        _set_lock_types(self, f"view:{allowed};search:{allowed};get:{allowed};drop:false();give:false()")

    def at_pre_get(self, getter, **kwargs):
        if getter.id != int(self.db.tutorial_owner_id or 0):
            getter.msg("That equipment belongs to another responder.")
            return False
        return super().at_pre_get(getter, **kwargs)

    def at_pre_drop(self, dropper, **kwargs):
        dropper.msg("Keep that with you until the distress response is resolved.")
        return False

    def at_pre_give(self, giver, getter, **kwargs):
        giver.msg("That item is tied to this distress response.")
        return False

    def at_get(self, getter, **kwargs):
        super().at_get(getter, **kwargs)
        from world.tutorial import handle_item_collected

        handle_item_collected(getter, self)


class PortableInductionBridge(TutorialQuestItem):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = (
            "Two insulated contact blocks are joined by a folded induction coil and a heavy "
            "locking handle. Stenciled instructions identify it as an emergency replacement "
            "for stripped or burned power links."
        )


class TransitRoutingWafer(TutorialQuestItem):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.calibrated = False
        self.db.desc = (
            "A rugged manual data wafer recovered from the SOS relay. Its origin field is "
            "corrupt, and it contains no usable destination handshake."
        )

    def get_display_desc(self, looker, **kwargs):
        if self.db.calibrated:
            return (
                "The wafer contains a current one-way handshake from an unnamed civilian "
                "receiver. Its source field remains permanently unreadable."
            )
        return super().get_display_desc(looker, **kwargs)


class SpareOxygenCanister(TutorialQuestItem):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.oxygen_remaining = 3600
        self.db.desc = (
            "A compact canister of compressed breathing mix with a universal suit fitting. "
            "Its seal is intact and its gauge reads sixty minutes at standard draw."
        )


class EmergencyMedPatch(TutorialQuestItem):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = (
            "A sealed adhesive patch containing clotting mesh, antiseptic, and a measured "
            "analgesic dose. It can stabilize ordinary trauma but makes no claim about parasites or unknown infection."
        )


class PersonalPortablePorter(TutorialOwnedMixin, EquipableItem):
    """A bound travel device and a conversational endpoint for Porter."""

    def at_object_creation(self):
        super().at_object_creation()
        self.db.equipment_slot = "wrist"
        self.db.equipped = False
        self.db.bound = False
        self.db.cosmetic_equipment = True
        self.db.desc = (
            "A narrow wrist device of black ceramic and scratched silver mesh, sized to close "
            "over a suit sleeve. Three nested rings form its only corporate mark. Beneath them, "
            "tiny letters spell PERSONAL PORTABLE PORTER. A recessed sensor waits beside UNBOUND."
        )

    def assign_tutorial_owner(self, character, instance_id, role):
        super().assign_tutorial_owner(character, instance_id, role)
        allowed = _owner_lock(character.id)
        _set_lock_types(self, f"view:{allowed};search:{allowed};get:{allowed};drop:false();give:false()")

    def get_display_desc(self, looker, **kwargs):
        if not self.db.bound:
            return super().get_display_desc(looker, **kwargs)
        state = "rests close around your wrist" if self.db.equipped else "recognizes you while carried"
        return (
            f"The Personal Portable Porter {state}. Its three pale rings track identity, route, "
            "and transport safety. Equipping it is cosmetic; Porter remains available while carried."
        )

    def equip_to(self, wearer, quiet=False):
        if not self.db.bound:
            if not quiet:
                wearer.msg("Porter must be bound before it will close around your wrist.")
            return False
        return super().equip_to(wearer, quiet=quiet)

    def at_pre_drop(self, dropper, **kwargs):
        dropper.msg("The bound Porter refuses to leave its registered traveler.")
        return False

    def at_pre_give(self, giver, getter, **kwargs):
        giver.msg("Porter's identity binding cannot be transferred by handing over the device.")
        return False

    def at_get(self, getter, **kwargs):
        super().at_get(getter, **kwargs)
        from world.tutorial import handle_item_collected

        handle_item_collected(getter, self)

    def at_talk(self, character, session=None):
        from world.tutorial import porter_conversation

        porter_conversation(character)

    def at_greet(self, character):
        character.msg('Porter says, "I am already bound to you. A formal greeting seems operationally redundant, but hello."')


class TutorialSurvivor(TutorialOwnedMixin, FriendlyNPC):
    """Mara or Juno before the final transformation."""

    dialogue_module = "world.tutorial_dialogue"

    def assign_tutorial_owner(self, character, instance_id, role):
        super().assign_tutorial_owner(character, instance_id, role)
        allowed = _owner_lock(character.id)
        _set_lock_types(self, f"view:{allowed};search:{allowed};get:false();puppet:false()")

    def get_display_desc(self, looker, **kwargs):
        progress = dict(getattr(looker.db, "tutorial_progress", None) or {}) if looker else {}
        role = str(self.db.tutorial_role or "")
        if role == "mara":
            if progress.get("mara_following"):
                return (
                    "Mara Venn stands inside a thin emergency suit, one gloved hand clamped over "
                    "the bandage beneath her sleeve. She stays close."
                )
            if progress.get("mara_bitten"):
                return (
                    "Mara presses a clean bandage around a fresh bite above her wrist. The paired "
                    "punctures match the old wound on Juno's arm. She does not pretend not to understand."
                )
            return (
                "Mara Venn is a lean human woman in a command uniform worn soft by several sleepless "
                "weeks. Rationing has sharpened her face. One hand stays near the SOS controls and the other near Juno's cot."
            )
        if progress.get("companion_transit_ready"):
            return (
                "Juno's tremor has spread through her shoulders. Dark lines have reached her neck, "
                "and her attention drifts toward sounds no one else can hear."
            )
        return (
            "Juno Rusk is a broad-shouldered human woman in the remains of a security uniform. Fever "
            "has left her face grey and wet. A thick bandage encloses her left forearm, and faint dark lines climb toward her elbow."
        )

    def at_character_entered(self, character):
        # The authored room-entry scene is handled once by world.tutorial.
        return


class TutorialHostile(TutorialOwnedMixin, HostileNPC):
    """Non-respawning encounter controlled by the character's tutorial state."""

    encounter_role = "hostile"

    def _sync_authored_aggression(self):
        """Upgrade persisted encounters when their authored behavior changes."""

        should_aggress = self.encounter_role == "overtaken_juno"
        if bool(self.db.aggressive) != should_aggress:
            self.db.aggressive = should_aggress

    def at_init(self):
        super().at_init()
        self._sync_authored_aggression()

    def at_object_creation(self):
        super().at_object_creation()
        # Hostile means attackable, not automatically aggressive. Tutorial
        # parasites remain occupied with the dead until a player strikes first.
        self.db.aggressive = False
        self.db.respawn_seconds = 0

    def at_character_entered(self, character):
        # This also repairs pre-change tutorial instances before the inherited
        # room-entry hook has a chance to engage them.
        self._sync_authored_aggression()
        return super().at_character_entered(character)

    def assign_tutorial_owner(self, character, instance_id, role=None):
        role = role or self.encounter_role
        super().assign_tutorial_owner(character, instance_id, role)
        allowed = _owner_lock(character.id)
        _set_lock_types(self, f"view:{allowed};search:{allowed};get:false();puppet:false()")

    def at_defeat(self, contributors):
        from world.tutorial import handle_tutorial_hostile_defeat

        handle_tutorial_hostile_defeat(self)


class CorpseFeeder(TutorialHostile):
    encounter_role = "corpse_feeder"

    def at_object_creation(self):
        super().at_object_creation()
        self.db.health_max = self.db.health_current = 38
        self.db.damage_min, self.db.damage_max = 4, 7
        self.db.evasion = 1
        self.db.attack_name = "a compressed, many-limbed pounce"
        self.db.telegraph_seconds = 2.8
        self.db.attack_interval = 4.5
        self.db.experience_reward = 35
        self.db.desc = (
            "The parasite is the length of a forearm when its hooked limbs unfold. A translucent "
            "body pulses around a dark gut while blunt feeding spines grip the corpse beneath it. "
            "Frost clouds its shell. It is wholly intent on feeding and does not react to your arrival."
        )


class FeedingKnot(TutorialHostile):
    encounter_role = "feeding_knot"

    def at_object_creation(self):
        super().at_object_creation()
        self.db.health_max = self.db.health_current = 62
        self.db.damage_min, self.db.damage_max = 6, 9
        self.db.evasion = 3
        self.db.attack_name = "three hooked bodies peeling away in concert"
        self.db.telegraph_seconds = 2.3
        self.db.attack_interval = 4.0
        self.db.experience_reward = 55
        self.db.desc = (
            "Several parasites have locked limbs around one another and the body beneath them. "
            "Thin membranes carry dark fluid toward a shared pulsing sac. None of the feeders looks up from the easy meal."
        )


class OvertakenRaider(TutorialHostile):
    encounter_role = "overtaken_raider"

    def at_object_creation(self):
        super().at_object_creation()
        self.db.health_max = self.db.health_current = 82
        self.db.damage_min, self.db.damage_max = 7, 11
        self.db.armor = 6
        self.db.evasion = 1
        self.db.attack_name = "a dead arm hauled backward for a crushing swing"
        self.db.telegraph_seconds = 3.0
        self.db.attack_interval = 4.6
        self.db.experience_reward = 80
        self.db.desc = (
            "The pirate suit should not move: its visor is opaque with dried blood and a breach "
            "gapes beneath the collar. Pale fibers enter there and tighten around the spine whenever the body turns."
        )


class OvertakenJuno(TutorialHostile):
    encounter_role = "overtaken_juno"

    def at_object_creation(self):
        super().at_object_creation()
        # This authored boss is the exception: her mutation scene explicitly
        # ends by forcing combat rather than waiting for player initiation.
        self.db.aggressive = True
        self.db.level = 2
        self.db.health_max = self.db.health_current = 105
        self.db.damage_min, self.db.damage_max = 8, 12
        self.db.armor = 5
        self.db.evasion = 4
        self.db.attack_name = "a breathless lunge across the command ring"
        self.db.telegraph_seconds = 2.2
        self.db.attack_interval = 3.8
        self.db.experience_reward = 120
        self.db.desc = (
            "Juno's old wound has opened beneath the discarded bandage. Dark veins stand across "
            "her throat, and pale threads draw her body into movements too sharp to be voluntary. "
            "Recognition flickers behind her eyes, never long enough to stop what controls her."
        )

    def at_combat_damage(self, attacker, amount, before, after):
        if self.db.mara_bite_played or after <= 0 or after > int(self.db.health_max or 1) // 2:
            return
        self.db.mara_bite_played = True
        from world.tutorial import handle_juno_bite

        handle_juno_bite(self, attacker)
