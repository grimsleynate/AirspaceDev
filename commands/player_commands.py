"""Commands available to a character inside the game world."""

from time import time

from evennia import create_object

from .command import Command


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


class CmdGreet(Command):
    """
    Greet a friendly character.

    Usage:
        greet <name>
    """

    key = "greet"
    locks = "cmd:all()"
    help_category = "Interaction"

    def func(self):
        target = _find_friendly_npc(self.caller, self.args.strip(), "greet")
        if target:
            target.at_greet(self.caller)


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

        player_attack(self.caller, target)


class CmdSkills(Command):
    """
    Review the active and passive skills granted by your specialization.

    Usage:
        skills
    """

    key = "skills"
    aliases = ["abilities"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        from world.combat import specialization_kit
        from world.resources import build_resource_payload

        kit = specialization_kit(self.caller)
        if not kit:
            self.caller.msg("Your specialization does not have a prototype combat kit yet.")
            return
        payload = build_resource_payload(self.caller)
        active = kit["active"]
        passive = kit["passive"]
        cooldowns = dict(self.caller.db.skill_cooldowns or {})
        remaining = max(0.0, float(cooldowns.get(active["key"], 0)) - time())
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

        active = find_active_skill(self.caller)
        if not active:
            self.caller.msg("Your specialization does not have a prototype active skill yet.")
            return
        raw = " ".join(self.args.strip().lower().replace("_", " ").split())
        labels = sorted(
            {
                active["key"].replace("_", " "),
                active["name"].lower(),
                *active.get("aliases", ()),
            },
            key=len,
            reverse=True,
        )
        target_query = raw
        for label in labels:
            if raw == label:
                target_query = ""
                break
            if raw.startswith(f"{label} "):
                target_query = raw[len(label):].strip()
                break
        target = None
        if target_query:
            target = self.caller.search(target_query, location=self.caller.location)
            if not target:
                return
        use_active_skill(self.caller, active["key"], hostile=target)


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
            f"{resources['character']['species']} · {resources['character']['career']} · "
            f"{resources['character']['specialization']}",
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
