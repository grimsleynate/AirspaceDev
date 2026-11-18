"""Benben account-level character management commands."""

from time import perf_counter

from twisted.internet import reactor

from evennia.commands.default.account import CmdCharDelete as DefaultCmdCharDelete
from evennia.contrib.rpg.character_creator.character_creator import ContribCmdIC
from evennia.utils import logger
from evennia.utils.evmenu import get_input


class CmdIC(ContribCmdIC):
    """Enter a character using its displayed number or its name."""

    def func(self):
        selection = self.args.strip()
        if selection.isdigit():
            characters = list(self.account.characters)
            index = int(selection) - 1
            if index < 0 or index >= len(characters):
                self.msg("That character number is not available. Use |wlook|n to see your characters.")
                return
            character = characters[index]
            if character.db.chargen_step:
                self.execute_cmd("charcreate")
                return
            self.args = character.key
        super().func()


class CmdCharDelete(DefaultCmdCharDelete):
    """Delete a character, report timing, and immediately redraw the roster."""

    def func(self):
        account = self.account
        if not self.args:
            self.msg("Usage: chardelete <charactername>")
            return
        matches = [
            character
            for character in account.characters
            if character.key.lower() == self.args.lower()
        ]
        if not matches:
            self.msg("You have no such character to delete.")
            return
        if len(matches) > 1:
            self.msg("Deletion aborted because more than one character has that name.")
            return
        character = matches[0]
        if not character.access(account, "delete"):
            self.msg("You do not have permission to delete this character.")
            return
        account.ndb._char_to_delete = character

        def _callback(caller, callback_prompt, result):
            target = caller.ndb._char_to_delete
            try:
                if result.strip().lower() != "yes":
                    caller.msg("Deletion was aborted.")
                    return

                started = perf_counter()
                key = target.key
                caller.characters.remove(target)
                target.delete()
                elapsed = perf_counter() - started
                caller.msg(f"Character '{key}' was permanently deleted ({elapsed:.2f}s).")

                logger.log_sec(...)
                logger.log_info(...)

            finally:
                if hasattr(caller.ndb, "_char_to_delete"):
                    del caller.ndb._char_to_delete

                # Run "look" AFTER the system command has fully exited
                reactor.callLater(0, caller.execute_cmd, "look", session=self.session)

        get_input(
            account,
            f"|rThis will permanently destroy '{character.key}'. This cannot be undone.|n Continue yes/[no]?",
            _callback,
        )
