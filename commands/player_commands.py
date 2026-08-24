"""Commands available to a character inside the game world."""

from time import time

from evennia import create_object
from evennia.commands.default.general import CmdInventory as DefaultCmdInventory
from evennia.utils import utils
from evennia.utils.ansi import raw as raw_ansi

from .command import Command


class CmdContainerSizes(Command):
    """
    Toggle dimensional container-fit checks (Admin only).

    Usage:
        containersizes
        containersizes on
        containersizes off
    """

    key = "containersizes"
    aliases = ["containersize", "sizesystem"]
    locks = "cmd:perm(Admin)"
    help_category = "Admin"

    def func(self):
        from typeclasses.items import (
            container_sizes_enabled,
            set_container_sizes_enabled,
        )

        option = self.args.strip().lower()
        if option not in {"", "on", "off"}:
            self.caller.msg("Usage: containersizes [on|off]")
            return
        enabled = container_sizes_enabled() if not option else option == "on"
        if option:
            set_container_sizes_enabled(enabled)
        state = "ON" if enabled else "OFF"
        explanation = (
            "items must fit the container's interior dimensions"
            if enabled
            else "item dimensions are ignored; count capacities still apply"
        )
        self.caller.msg(f"Container size system is {state}: {explanation}.")


class CmdInventory(DefaultCmdInventory):
    """List carried, unequipped items; equipped gear is shown by ``equipment``."""

    def func(self):
        inventory_items = getattr(
            self.caller, "inventory_items", lambda: self.caller.contents
        )()
        if not inventory_items:
            string = "You are not carrying anything. Use |wequipment|n to view equipped gear."
        else:
            table = self.styled_table(border="header")
            for key, desc, _ in utils.group_objects_by_key_and_desc(
                inventory_items, caller=self.caller
            ):
                table.add_row(
                    f"|C{key}|n",
                    f"{utils.crop(raw_ansi(desc or ''), width=50) or ''}|n",
                )
            count = len(inventory_items)
            capacity = int(getattr(self.caller, "inventory_capacity", 0) or 0)
            count_label = f" ({count}/{capacity})" if capacity else ""
            string = f"|wYou are carrying{count_label}:\n{table}"
        self.msg(text=(string, {"type": "inventory"}))
        from world.opening_tutorial import record_tutorial_proof

        record_tutorial_proof(self.caller, "inventory_checked")


def _find_friendly_npc(caller, query, verb):
    """Find a visible object which supports the requested interaction."""

    if not query:
        caller.msg(f"{verb.capitalize()} whom?")
        return None
    candidates = list(caller.contents)
    if caller.location:
        candidates.extend(caller.location.contents)
    target = caller.search(query, candidates=candidates)
    if not target:
        return None
    if not getattr(target, f"at_{verb}", None):
        caller.msg(f"{target.get_display_name(caller)} does not respond.")
        return None
    return target


def _find_social_target(caller, query):
    """Find a visible room occupant for a social interaction."""

    if not query:
        caller.msg("Greet whom?")
        return None
    return caller.search(query, location=caller.location)


class CmdGreet(Command):
    """
    Greet a friendly character.

    Usage:
        greet <name>
        nod|wave|smile|bow|salute <name>
    """

    key = "greet"
    aliases = ["nod", "wave", "smile", "bow", "salute"]
    locks = "cmd:all()"
    help_category = "Interaction"

    def func(self):
        social = str(self.cmdstring or self.key).lower()
        target = _find_social_target(self.caller, self.args.strip())
        if not target:
            return
        if getattr(target, "at_greet", None):
            target.at_greet(self.caller, session=self.session, social=social)
            return
        phrase = {
            "greet": "$conj(greet)",
            "nod": "$conj(nod) to",
            "wave": "$conj(wave) to",
            "smile": "$conj(smile) at",
            "bow": "$conj(bow) to",
            "salute": "$conj(salute)",
        }.get(social, "$conj(greet)")
        self.caller.location.msg_contents(
            f"$You() {phrase} {target.key}.", from_obj=self.caller
        )


class CmdTalk(Command):
    """
    Start a conversation with a friendly character.

    Usage:
        talk <name>
        talk to <name>
    """

    key = "talk"
    locks = "cmd:all()"
    help_category = "Interaction"

    def func(self):
        query = self.args.strip()
        if query.lower().startswith("to "):
            query = query[3:].strip()
        target = _find_friendly_npc(self.caller, query, "talk")
        if target:
            target.at_talk(self.caller, session=self.session)


class CmdMap(Command):
    """
    Control the automatic ASCII room map.

    Usage:
        map
        map on
        map off
        map reset
        map reset confirm

    With no argument, this displays the current map once. ``map on`` puts
    the map above every room description; ``map off`` hides it. The setting
    is saved separately on each character. ``map reset`` permanently clears
    that character's explored graphical map after confirmation.
    """

    key = "map"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        option = self.args.strip().lower()

        if option == "on":
            from world.accessibility import get_accessibility_preferences

            preferences = get_accessibility_preferences(caller.account)
            if not preferences["ascii_maps"]:
                caller.msg(
                    "ASCII maps are disabled by your account accessibility settings. "
                    "Use CONFIG MAPS ON after turning screen-reader mode off."
                )
                return
            caller.db.ascii_map_enabled = True
            caller.msg("|gASCII map enabled.|n It will appear whenever you move or look.")
            return

        if option == "off":
            caller.db.ascii_map_enabled = False
            caller.msg("|yASCII map disabled.|n Use |wmap on|n to restore it.")
            return

        if option == "reset":
            caller.msg(
                "This will permanently forget this character's explored map. "
                "Use |wmap reset confirm|n to continue."
            )
            return

        if option == "reset confirm":
            from world.mapping import clear_character_map, send_map_sync

            clear_character_map(caller, keep_current=True)
            send_map_sync(caller)
            caller.msg("|gExplored map reset.|n Your current room remains known.")
            return

        if option:
            caller.msg(
                "Usage: |wmap|n, |wmap on|n, |wmap off|n, or |wmap reset|n"
            )
            return

        location = caller.location
        if not location or not hasattr(location, "get_ascii_map"):
            caller.msg("There is no local map to display here.")
            return

        from world.accessibility import ascii_maps_enabled

        if not ascii_maps_enabled(caller):
            caller.msg(
                "ASCII maps are disabled by your accessibility settings. "
                "Use CONFIG MAPS ON after turning screen-reader mode off."
            )
            return

        caller.msg(location.get_ascii_map(caller))


class CmdVitals(Command):
    """
    Show health, the career resource, and life support.

    Usage:
        vitals
        status
    """

    key = "vitals"
    aliases = ["status"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        from world.resources import build_resource_payload

        payload = build_resource_payload(self.caller)
        health = payload["health"]
        primary = payload["primary"]
        lines = [
            f"|wHealth:|n {health['current']}/{health['max']}",
            f"|w{primary['label']}:|n {primary['current']}/{primary['max']}",
        ]
        oxygen = payload["oxygen"]
        if oxygen is not None:
            source = oxygen["source"] or "no equipped source"
            lines.append(f"|wOxygen:|n {oxygen['current']}/{oxygen['max']} ({source})")
        self.caller.msg("\n".join(lines))


class CmdOxygen(Command):
    """
    Check your equipped breathable supply.

    Usage:
        oxygen
    """

    key = "oxygen"
    aliases = ["o2", "air"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        from world.resources import build_resource_payload, is_synth

        if is_synth(self.caller):
            self.caller.msg("Your synthetic body does not require oxygen.")
            return
        payload = build_resource_payload(self.caller)
        oxygen = payload["oxygen"]
        if not oxygen or not oxygen["source"]:
            self.caller.msg("|rYou have no equipped oxygen source.|n")
            return
        minutes, seconds = divmod(int(oxygen["current"]), 60)
        state = "supplying you" if oxygen["active"] else "on standby"
        self.caller.msg(
            f"|w{oxygen['source']}:|n {minutes}:{seconds:02d} remaining; {state}."
        )


class CmdEquipment(Command):
    """
    List equipped gear.

    Usage:
        equipment
        gear
    """

    key = "equipment"
    aliases = ["gear", "eq"]
    locks = "cmd:all()"
    help_category = "Equipment"

    def func(self):
        from world.resources import is_synth

        equipped = [
            item
            for item in self.caller.contents
            if getattr(item, "is_equipped", False)
        ]
        lines = ["|wEquipped:|n"]
        if equipped:
            for item in sorted(equipped, key=lambda obj: obj.equipment_slot):
                slot = item.equipment_slot.replace("_", " ").title()
                detail = ""
                if getattr(item, "provides_oxygen", False):
                    remaining = max(0, int(item.db.oxygen_remaining or 0))
                    minutes, seconds = divmod(remaining, 60)
                    detail = f" — {minutes}:{seconds:02d} oxygen"
                combat_stats = getattr(item, "combat_stat_summary", lambda: "")()
                if combat_stats:
                    detail += f" — {combat_stats}"
                lines.append(f"  |w{slot}:|n {item.get_display_name(self.caller)}{detail}")
        else:
            lines.append("  Nothing.")
        if is_synth(self.caller):
            lines.append("|cLife support:|n Oxygen not required by Synth physiology.")
        self.caller.msg("\n".join(lines))
        from world.opening_tutorial import record_tutorial_proof

        record_tutorial_proof(self.caller, "equipment_checked")


class CmdEquip(Command):
    """
    Equip a carried item.

    Usage:
        equip <item>
    """

    key = "equip"
    locks = "cmd:all()"
    help_category = "Equipment"

    def func(self):
        query = self.args.strip()
        if not query:
            self.caller.msg("Usage: |wequip <item>|n")
            return
        item = self.caller.search(query, candidates=self.caller.contents)
        if not item:
            return
        equip = getattr(item, "equip_to", None)
        if not equip:
            self.caller.msg(f"{item.get_display_name(self.caller)} cannot be equipped.")
            return
        equip(self.caller)


class CmdUnequip(Command):
    """
    Unequip an item without dropping it.

    Usage:
        unequip <item>
    """

    key = "unequip"
    locks = "cmd:all()"
    help_category = "Equipment"

    def func(self):
        query = self.args.strip()
        if not query:
            self.caller.msg("Usage: |wunequip <item>|n")
            return
        item = self.caller.search(query, candidates=self.caller.contents)
        if not item:
            return
        unequip = getattr(item, "unequip_from", None)
        if not unequip:
            self.caller.msg(f"{item.get_display_name(self.caller)} is not equipment.")
            return
        unequip(self.caller)


class _CmdNumpad(Command):
    """Translate a numeric keypad command into ordinary movement or look."""

    destination_command = "look"
    locks = "cmd:all()"
    help_category = "Movement"
    auto_help = False

    def func(self):
        self.caller.execute_cmd(self.destination_command, session=self.session)


class CmdNumpadNorthwest(_CmdNumpad):
    key = "7"
    aliases = ["numpad7", "kp7"]
    destination_command = "northwest"


class CmdNumpadNorth(_CmdNumpad):
    key = "8"
    aliases = ["numpad8", "kp8"]
    destination_command = "north"


class CmdNumpadNortheast(_CmdNumpad):
    key = "9"
    aliases = ["numpad9", "kp9"]
    destination_command = "northeast"


class CmdNumpadWest(_CmdNumpad):
    key = "4"
    aliases = ["numpad4", "kp4"]
    destination_command = "west"


class CmdNumpadLook(_CmdNumpad):
    key = "5"
    aliases = ["numpad5", "kp5"]
    destination_command = "look"


class CmdNumpadEast(_CmdNumpad):
    key = "6"
    aliases = ["numpad6", "kp6"]
    destination_command = "east"


class CmdNumpadSouthwest(_CmdNumpad):
    key = "1"
    aliases = ["numpad1", "kp1"]
    destination_command = "southwest"


class CmdNumpadSouth(_CmdNumpad):
    key = "2"
    aliases = ["numpad2", "kp2"]
    destination_command = "south"


class CmdNumpadSoutheast(_CmdNumpad):
    key = "3"
    aliases = ["numpad3", "kp3"]
    destination_command = "southeast"


class CmdSoundTest(Command):
    """
    Trigger native-client audio while building and testing.

    Usage:
        soundtest
        soundtest <confirm|objective|door|terminal|hurt|attack|scene>

    This builder-only command verifies the semantic event pipeline without
    coupling game commands to media filenames.
    """

    key = "soundtest"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    EVENTS = {
        "confirm": "ui.confirm",
        "objective": "ui.objective_complete",
        "door": "world.door_open",
        "terminal": "world.terminal",
        "hurt": "combat.player_hurt",
        "attack": "combat.energy_attack",
    }

    def func(self):
        choice = self.args.strip().lower()
        if not choice:
            self.caller.msg("Usage: soundtest <confirm|objective|door|terminal|hurt|attack|scene>")
            return

        if choice == "scene":
            from world.audio import send_audio_scene

            send_audio_scene(self.caller, force=True)
            self.caller.msg("Current audio scene sent to supported web sessions.")
            return

        event = self.EVENTS.get(choice)
        if not event:
            self.caller.msg("Unknown sound. Choose confirm, objective, door, terminal, hurt, attack, or scene.")
            return

        from world.audio import emit_audio

        emit_audio(self.caller, event)
        self.caller.msg(f"Audio event sent: {event}")


class CmdAttack(Command):
    """
    Start automatically attacking a hostile with your equipped weapon.

    Usage:
        attack <target>
        kill <target>

    Basic attacks continue at the weapon's recovery cadence. Cast skills
    manually between them. Moving away disengages during this prototype phase.
    """

    key = "attack"
    aliases = ["kill"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        query = self.args.strip()
        if not query:
            self.caller.msg("Attack what?")
            return
        target = self.caller.search(query, location=self.caller.location)
        if not target:
            return
        from world.combat import player_attack

        if getattr(target, "is_hostile", False):
            from world.opening_tutorial import record_tutorial_proof

            record_tutorial_proof(self.caller, "attack_started")
        player_attack(self.caller, target)


class CmdSkills(Command):
    """
    Review your Background miniskill and active Ability Trees.

    Usage:
        skills
    """

    key = "skills"
    aliases = ["abilities"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        from world.character_options import ABILITY_TREES, BACKGROUNDS, MINISKILLS, STARTER_TREE_ABILITIES

        active_trees = list(self.caller.db.active_skill_trees or [])
        if active_trees:
            from world.character_traits import ability_tree_progress

            background = BACKGROUNDS.get(self.caller.db.background, {})
            miniskill = MINISKILLS.get(background.get("miniskill"), {})
            lines = ["|h|wAbilities|n"]
            if miniskill:
                lines.extend((
                    f"|yBackground miniskill — {miniskill['name']}:|n {miniskill['description']}",
                    "",
                ))
            lines.append("|h|wActive Ability Trees|n")
            for tree_key in active_trees:
                tree = ABILITY_TREES.get(tree_key, {"name": tree_key.title(), "description": ""})
                skill = STARTER_TREE_ABILITIES.get(tree_key)
                proficiency, experience = ability_tree_progress(self.caller, tree_key)
                lines.append(f"|c{tree['name']}|n — proficiency {proficiency} · practice {experience}")
                lines.append(f"  {tree['description']}")
                if skill:
                    lines.append(f"  |g{skill['name']}|n: {skill['description']}")
                    lines.append(f"  Use: |wcast {skill['key'].replace('_', ' ')} [target]|n")
            known = list(self.caller.db.known_skill_trees or active_trees)
            inactive = [key for key in known if key not in active_trees]
            if inactive:
                lines.append("|wKnown but inactive Ability Trees:|n " + ", ".join(ABILITY_TREES.get(key, {"name": key})["name"] for key in inactive))
            self.caller.msg("\n".join(lines))
            return
        from world.combat import specialization_kit
        from world.resources import build_resource_payload

        kit = specialization_kit(self.caller)
        if not kit:
            self.caller.msg("Your specialization does not have a prototype combat kit yet.")
            return
        payload = build_resource_payload(self.caller)
        active = kit["active"]
        passive = kit["passive"]
        remaining = self.caller.cooldowns.time_left(active["key"])
        readiness = "ready" if not remaining else f"{remaining:.1f}s cooldown"
        self.caller.msg(
            "\n".join(
                (
                    f"|h|w{payload['character']['specialization']} Skills|n",
                    f"|gPassive — {passive['name']}:|n {passive['description']}",
                    f"|cActive — {active['name']}:|n {active['description']}",
                    f"  Cost {active['cost']} {payload['primary']['label']} · "
                    f"Cooldown {active['cooldown']:.0f}s · {readiness}",
                    f"  Use: |wcast {active['key'].replace('_', ' ')} [target]|n",
                )
            )
        )


class CmdInnate(Command):
    """Use the sensory or memory technique granted by your species."""

    key = "innate"
    aliases = ["spectrum", "imprint", "resonate", "presence"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        from world.character_options import SPECIES

        species = SPECIES.get(self.caller.db.species, {})
        benefit = species.get("benefit", {})
        expected = benefit.get("command")
        invoked = str(self.cmdstring or "").lower()
        if not expected:
            self.caller.msg(f"{benefit.get('name', 'Your species benefit')} is passive: {benefit.get('description', '')}")
            return
        if invoked == "innate":
            self.caller.msg(f"Use |w{expected}|n: {benefit['description']}")
            return
        if invoked != expected:
            self.caller.msg(f"Your innate technique is |w{expected}|n, not {invoked}.")
            return

        if expected == "spectrum":
            target = self.caller.search(self.args.strip(), location=self.caller.location) if self.args.strip() else self.caller.location
            if not target:
                return
            detail = target.db.spectrum_desc or (
                "Heat residue, reflected station light, and ordinary pigment separate into layers, "
                "but nothing here carries an authored spectrum clue."
            )
            self.caller.msg(f"|mSpectrum Reading — {target.get_display_name(self.caller)}|n\n{detail}")
            return

        if expected == "imprint":
            if self.args.strip().lower() == "recall":
                memory = dict(self.caller.db.serev_imprint or {})
                if not memory:
                    self.caller.msg("You have not preserved an imprint yet.")
                else:
                    self.caller.msg(f"|mImprint — {memory['name']}|n\n{memory['description']}")
                return
            location = self.caller.location
            if not location:
                self.caller.msg("There is no stable scene to imprint.")
                return
            self.caller.db.serev_imprint = {
                "name": location.get_display_name(self.caller),
                "description": location.get_display_desc(self.caller),
                "location_id": location.id,
            }
            self.caller.msg("You and your mantle commit the present scene as your one deliberate imprint.")
            return

        if expected == "resonate":
            target = self.caller.search(self.args.strip(), location=self.caller.location) if self.args.strip() else self.caller.location
            if not target:
                return
            detail = target.db.resonance_desc or (
                "Its heat and stress answer in ordinary patterns; no authored resonance clue stands out."
            )
            self.caller.msg(f"|mResonance — {target.get_display_name(self.caller)}|n\n{detail}")
            return

        occupants = [
            obj.get_display_name(self.caller) for obj in self.caller.location.contents
            if obj is not self.caller and (
                getattr(obj, "has_account", False)
                or getattr(obj, "is_npc", False)
                or getattr(obj, "is_hostile", False)
            )
        ] if self.caller.location else []
        if occupants:
            self.caller.msg("Directed living attention presses against your sail from: " + ", ".join(occupants) + ".")
        else:
            self.caller.msg("Your sail finds no distinct living attention beyond your own.")


class CmdSkill(Command):
    """
    Cast your specialization's active combat skill.

    Usage:
        cast <skill name>
        cast <skill name> [target]
        c <skill name> [target]

    With no named target, the skill uses your current combat target. A cast
    postpones the next automatic basic attack rather than waiting behind it.
    """

    key = "cast"
    aliases = ["c", "skill", "ability"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        from world.combat import find_active_skill, use_active_skill
        from world.character_options import STARTER_TREE_ABILITIES

        active_trees = list(self.caller.db.active_skill_trees or [])
        available = [
            {**STARTER_TREE_ABILITIES[key], "tree_key": key}
            for key in active_trees if key in STARTER_TREE_ABILITIES
        ]
        if not available:
            active = find_active_skill(self.caller)
            available = [active] if active else []
        if not available:
            self.caller.msg("You have no active-tree ability available yet.")
            return
        raw = " ".join(self.args.strip().lower().replace("_", " ").split())
        selected = None
        target_query = ""
        for candidate in available:
            labels = sorted({candidate["key"].replace("_", " "), candidate["name"].lower(), *candidate.get("aliases", ())}, key=len, reverse=True)
            for label in labels:
                if raw == label or raw.startswith(f"{label} "):
                    selected = candidate
                    target_query = raw[len(label):].strip()
                    break
            if selected:
                break
        if not selected:
            self.caller.msg("Name an active ability first. Use |wskills|n to review your commands.")
            return
        target = None
        if target_query:
            target = self.caller.search(target_query, location=self.caller.location)
            if not target:
                return
        use_active_skill(self.caller, selected["key"], hostile=target)


class CmdSheet(Command):
    """
    Show level, experience, combat stats, and equipped weapon.

    Usage:
        sheet
        score
    """

    key = "sheet"
    aliases = ["score", "level"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        from world.combat import character_combat_stats, progression_payload, specialization_kit
        from world.resources import build_resource_payload

        progression = progression_payload(self.caller)
        resources = build_resource_payload(self.caller)
        stats = character_combat_stats(self.caller)
        kit = specialization_kit(self.caller)
        next_xp = (
            "maximum level"
            if progression["next_level_at"] is None
            else f"{progression['level_experience']}/{progression['level_experience_max']} this level"
        )
        lines = [
            f"|h|w{self.caller.key} — Level {progression['level']}|n",
            (
                f"{resources['character']['species']} · {resources['character']['background']}\n"
                f"|wActive practice:|n {', '.join(resources['character']['active_skill_trees'])}"
                if self.caller.db.chargen_complete
                else f"{resources['character']['species']} · {resources['character']['career']} · {resources['character']['specialization']}"
            ),
            (
                f"|wPre-Synth Gender:|n "
                f"{str(resources['character']['pre_synth_gender']).replace('_', ' ').title()}"
                if resources['character']['species'].lower() == "synth"
                else f"|wGender:|n {str(resources['character']['gender']).replace('_', ' ').title()}"
            ),
            f"|wExperience:|n {progression['experience']} total ({next_xp})",
            f"|wHealth:|n {resources['health']['current']}/{resources['health']['max']}  "
            f"|w{resources['primary']['label']}:|n {resources['primary']['current']}/{resources['primary']['max']}",
            f"|wWeapon:|n {stats['weapon_name']} ({stats['damage_min']}–{stats['damage_max']} damage)",
            f"|wCombat:|n Armor {stats['armor']} · Accuracy {stats['accuracy']:+d} · "
            f"Evasion {stats['evasion']} · Crit {stats['crit_chance']}%",
        ]
        if kit:
            lines.append(f"|wSkills:|n {kit['passive']['name']} (passive), {kit['active']['name']} (active)")
        self.caller.msg("\n".join(lines))


class CmdConsider(Command):
    """Estimate a hostile's danger relative to your current level."""

    key = "consider"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        query = self.args.strip()
        if not query:
            self.caller.msg("Consider what?")
            return
        target = self.caller.search(query, location=self.caller.location)
        if not target:
            return
        if not getattr(target, "is_hostile", False):
            self.caller.msg(f"{target.get_display_name(self.caller)} is not a combat target.")
            return
        player_level = int(self.caller.db.level or 1)
        target_level = int(target.db.level or 1)
        difference = target_level - player_level
        verdict = (
            "should be an easy fight"
            if difference <= -2
            else "looks manageable"
            if difference <= 0
            else "will be a serious challenge"
            if difference <= 2
            else "is overwhelmingly dangerous"
        )
        self.caller.msg(
            f"|h|r{target.key}|n is level {target_level} and {verdict}. "
            f"Condition: {int(target.db.health_current or 0)}/{int(target.db.health_max or 1)}."
        )
        from world.opening_tutorial import record_tutorial_proof

        record_tutorial_proof(self.caller, "target_considered")


class CmdCombatDemo(Command):
    """
    Prepare and reset the early combat proving ground.

    Usage:
        combatdemo kit
        combatdemo spawn <drone|parasite|armored>
        combatdemo reset
    """

    key = "combatdemo"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        option, _, argument = self.args.strip().lower().partition(" ")
        if option == "kit":
            from typeclasses.items import ensure_starter_combat_gear
            from world.resources import send_character_resources

            ensure_starter_combat_gear(self.caller)
            send_character_resources(self.caller, force=True)
            self.caller.msg("Starter combat kit reconciled. Use |wequipment|n and |wsheet|n to inspect it.")
            return
        if option == "spawn":
            from typeclasses.npcs import ArmoredScavenger, ScavengerParasite, TrainingDrone

            choices = {
                "drone": (TrainingDrone, "training security drone", ["drone", "training drone"]),
                "parasite": (ScavengerParasite, "scavenger parasite", ["parasite", "scavenger"]),
                "armored": (ArmoredScavenger, "armored scavenger", ["armored", "scavenger"]),
            }
            definition = choices.get(argument)
            if not definition:
                self.caller.msg("Choose drone, parasite, or armored.")
                return
            typeclass, key, aliases = definition
            monster = create_object(typeclass, key=key, aliases=aliases, location=self.caller.location, home=self.caller.location)
            monster.tags.add("combat_demo", category="quasar_content")
            self.caller.location.msg_contents(f"|h|r{monster.key}|n enters the proving ground.")
            return
        if option == "reset":
            from world.combat import leave_combat, reset_hostile
            from world.resources import restore_health, restore_primary_resource

            leave_combat(self.caller)
            restore_health(self.caller)
            restore_primary_resource(self.caller)
            for obj in self.caller.location.contents:
                if getattr(obj, "is_hostile", False):
                    reset_hostile(obj, announce=False)
            self.caller.msg("Your resources and all hostiles here have been reset.")
            return
        self.caller.msg("Usage: |wcombatdemo kit|n, |wcombatdemo spawn <drone|parasite|armored>|n, or |wcombatdemo reset|n")
