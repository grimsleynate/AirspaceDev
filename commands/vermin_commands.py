"""Commands for the optional ambient-vermin awareness channel."""

from commands.command import Command


class CmdVermin(Command):
    """Toggle unobtrusive alerts when city vermin are nearby.

    Usage:
        vermin
        vermin on|off|status

    Vermin remain visible and attackable regardless of this setting. The
    toggle only controls arrival and spawn alerts, and defaults to off.
    """

    key = "vermin"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        option = self.args.strip().lower()
        current = bool(self.caller.db.vermin_awareness)
        if option not in {"", "on", "off", "status"}:
            self.caller.msg("Usage: |wvermin [on|off|status]|n")
            return
        if option == "status":
            self.caller.msg(
                f"Vermin awareness is {'|gON|n' if current else '|xOFF|n'}."
            )
            return
        enabled = not current if not option else option == "on"
        self.caller.db.vermin_awareness = enabled
        if enabled:
            self.caller.msg(
                "|gVermin awareness enabled.|n City vermin will now produce brief presence alerts."
            )
            from world.vermin import notify_vermin_presence

            notify_vermin_presence(self.caller)
        else:
            self.caller.msg(
                "|xVermin awareness disabled.|n Vermin remain visible and attackable, but alerts are suppressed."
            )

