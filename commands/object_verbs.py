"""Bespoke verbs carried by objects instead of the global command set.

An object exposes a verb by holding a cmdset whose commands subclass
``ObjectVerbCommand``. Evennia merges the cmdsets of objects in the caller's
room (and inventory) through each object's ``call`` lock, so the verb works as
text. ``client_label`` makes ``ObjectParent.get_client_actions`` offer the same
command in the web client's context menu as ``<key> #<id>``.

Example::

    class CmdPress(ObjectVerbCommand):
        key = "press"
        client_label = "Press"

        def func(self):
            self.caller.msg(f"You press {self.obj.key}.")

    class ButtonCmdSet(CmdSet):
        def at_cmdset_creation(self):
            self.add(CmdPress())

    button.cmdset.add(ButtonCmdSet, persistent=True)
"""

from evennia.commands.command import Command


class ObjectVerbCommand(Command):
    """A command provided by ``self.obj``, the object carrying the cmdset."""

    client_label = None  # set to show the verb in the web client
    locks = "cmd:all()"
    auto_help = False

    def parse(self):
        # Accept "press", "press button" or "press #12": the verb is already
        # bound to self.obj, so any argument only disambiguates.
        self.target_ref = self.args.strip()

    def targets_this_object(self):
        """True when the argument is empty or names ``self.obj``."""

        ref = self.target_ref
        if not ref:
            return True
        if ref.lstrip("#").isdigit():
            return int(ref.lstrip("#")) == self.obj.id
        return ref.lower() in {self.obj.key.lower(), *map(str.lower, self.obj.aliases.all())}
