"""Commands available to a character inside the game world."""

from time import time

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
    Show health and progression.

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
        progression = payload["progression"]
        self.caller.msg(
            f"|wHealth:|n {health['current']}/{health['max']}\n"
            f"|wLevel:|n {progression['level']} ({progression['experience']} XP)"
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
                combat_stats = getattr(item, "combat_stat_summary", lambda: "")()
                if combat_stats:
                    detail = f" — {combat_stats}"
                lines.append(f"  |w{slot}:|n {item.get_display_name(self.caller)}{detail}")
        else:
            lines.append("  Nothing.")
        self.caller.msg("\n".join(lines))


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
        soundtest <confirm|objective|door|hurt|attack|scene>

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
        "hurt": "combat.player_hurt",
        "attack": "combat.attack",
    }

    def func(self):
        choice = self.args.strip().lower()
        if not choice:
            self.caller.msg("Usage: soundtest <confirm|objective|door|hurt|attack|scene>")
            return

        if choice == "scene":
            from world.audio import send_audio_scene

            send_audio_scene(self.caller, force=True)
            self.caller.msg("Current audio scene sent to supported web sessions.")
            return

        event = self.EVENTS.get(choice)
        if not event:
            self.caller.msg("Unknown sound. Choose confirm, objective, door, hurt, attack, or scene.")
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

    Basic attacks continue at the weapon's recovery cadence. Moving away
    disengages.
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

        player_attack(self.caller, target)


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
        from world.combat import character_combat_stats, progression_payload
        from world.resources import build_resource_payload

        progression = progression_payload(self.caller)
        resources = build_resource_payload(self.caller)
        stats = character_combat_stats(self.caller)
        next_xp = (
            "maximum level"
            if progression["next_level_at"] is None
            else f"{progression['level_experience']}/{progression['level_experience_max']} this level"
        )
        lines = [
            f"|h|w{self.caller.key} — Level {progression['level']}|n",
            f"|wExperience:|n {progression['experience']} total ({next_xp})",
            f"|wHealth:|n {resources['health']['current']}/{resources['health']['max']}",
            f"|wWeapon:|n {stats['weapon_name']} ({stats['damage_min']}–{stats['damage_max']} damage)",
            f"|wCombat:|n Armor {stats['armor']} · Accuracy {stats['accuracy']:+d} · "
            f"Evasion {stats['evasion']} · Crit {stats['crit_chance']}%",
        ]
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
        from typeclasses.objects import attackable_by

        if not attackable_by(target, self.caller):
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
        from world.health import health_of

        current, maximum = health_of(target)
        self.caller.msg(
            f"|h|r{target.key}|n is level {target_level} and {verdict}. "
            f"Condition: {current}/{maximum}."
        )
