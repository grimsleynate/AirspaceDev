"""Account-wide accessibility configuration available OOC and in character."""

from .command import Command


class CmdAccessibility(Command):
    """
    Configure screen-reader, color, map, and ambient-media accessibility.

    Usage:
        config
        config screenreader on|off
        config color auto|ansi|256|truecolor|off
        config effects on|off
        config maps on|off

    ``accessibility`` and ``access`` are aliases. Screen-reader mode strips
    ANSI and decorative transport output and disables ASCII maps plus room
    audio and visual effects. It does not shorten room descriptions.
    """

    key = "config"
    aliases = ["accessibility", "access", "screenreader"]
    locks = "cmd:all()"
    help_category = "Accessibility"
    account_caller = True

    def _status(self, preferences):
        state = lambda value: "on" if value else "off"
        return (
            "Accessibility settings\n"
            f"Screen reader: {state(preferences['screenreader'])}\n"
            f"Color: {preferences['color_mode']}\n"
            f"Room audio and visuals: {state(preferences['room_effects'])}\n"
            f"ASCII maps: {state(preferences['ascii_maps'])}\n"
            "Use HELP CONFIG for commands. These settings apply to every character."
        )

    def func(self):
        from world.accessibility import (
            COLOR_MODES,
            apply_to_account_sessions,
            get_accessibility_preferences,
            set_accessibility_preferences,
        )

        account = self.caller
        preferences = get_accessibility_preferences(account)
        parts = self.args.lower().split()
        if str(self.cmdstring).lower() == "screenreader" and not parts:
            parts = [
                "screenreader",
                "off" if preferences["screenreader"] else "on",
            ]
        if not parts:
            self.msg(self._status(preferences))
            return
        setting = {"ansi": "color", "map": "maps", "media": "effects"}.get(
            parts[0], parts[0]
        )
        value = parts[1] if len(parts) > 1 else None
        if setting == "screenreader":
            if value not in {"on", "off"}:
                self.msg("Usage: config screenreader on|off")
                return
            preferences = set_accessibility_preferences(
                account, screenreader=value == "on"
            )
        elif setting == "color":
            value = "auto" if value == "on" else value
            if value not in COLOR_MODES:
                self.msg("Usage: config color auto|ansi|256|truecolor|off")
                return
            if preferences["screenreader"] and value != "off":
                self.msg("Turn screen-reader mode off before enabling color.")
                return
            preferences = set_accessibility_preferences(account, color_mode=value)
        elif setting in {"effects", "maps"}:
            if value not in {"on", "off"}:
                self.msg(f"Usage: config {setting} on|off")
                return
            if preferences["screenreader"] and value == "on":
                self.msg(f"Turn screen-reader mode off before enabling {setting}.")
                return
            key = "room_effects" if setting == "effects" else "ascii_maps"
            preferences = set_accessibility_preferences(account, **{key: value == "on"})
        else:
            self.msg("Unknown setting. Use CONFIG or HELP CONFIG.")
            return

        preferences = apply_to_account_sessions(account)
        self.msg(self._status(preferences))
