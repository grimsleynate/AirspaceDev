"""Commands available to a character inside the game world."""

from .command import Command


def _find_friendly_npc(caller, query, verb):
    """Find a visible object which supports the requested interaction."""

    if not query:
        caller.msg(f"{verb.capitalize()} whom?")
        return None
    target = caller.search(query, location=caller.location)
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
