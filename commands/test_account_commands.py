"""Tests for numbered OOC character selection."""

from unittest.mock import patch

from evennia.utils.test_resources import EvenniaCommandTest

from commands.account_commands import CmdCharDelete, CmdIC


class NumberedCharacterSelectionTests(EvenniaCommandTest):
    def test_invalid_number_is_explained(self):
        result = self.call(CmdIC(), "99", caller=self.account, msg=None)

        self.assertIn("character number is not available", result)

    def test_completed_character_number_resolves_to_name(self):
        self.char1.db.chargen_step = None
        self.account.characters.add(self.char1)
        command = CmdIC()

        self.call(command, "1", caller=self.account, msg=None)

        self.assertEqual(command.args, self.char1.key)

    def test_character_deletion_redraws_account_roster(self):
        self.account.characters.add(self.char1)
        command = CmdCharDelete()

        with patch("commands.account_commands.get_input") as prompt:
            self.call(command, self.char1.key, caller=self.account, msg=None)

        callback = prompt.call_args.args[2]
        with patch.object(self.account, "execute_cmd") as execute:
            callback(self.account, "confirm", "yes")

        self.assertIsNone(self.char1.pk)
        execute.assert_called_once_with("look", session=command.session)
