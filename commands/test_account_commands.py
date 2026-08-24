"""Tests for numbered OOC character selection."""

from unittest.mock import patch

from evennia.contrib.base_systems.components import ComponentHolderMixin
from evennia.contrib.rpg.character_creator.character_creator import ContribCmdCharCreate
from evennia.utils.test_resources import EvenniaCommandTest

from commands.account_commands import CmdCharDelete, CmdIC
from commands.accessibility_commands import CmdAccessibility
from typeclasses.characters import Character
from typeclasses.items import PortableItem


class NumberedCharacterSelectionTests(EvenniaCommandTest):
    def test_accessibility_config_is_account_wide_and_plain_text(self):
        result = self.call(
            CmdAccessibility(), "screenreader on", caller=self.account, msg=None
        )

        preferences = self.account.db.accessibility_preferences
        self.assertTrue(preferences["screenreader"])
        self.assertFalse(preferences["room_effects"])
        self.assertIn("Screen reader: on", result)

    def test_screenreader_alias_toggles_the_profile(self):
        self.call(
            CmdAccessibility(), "", caller=self.account, cmdstring="screenreader", msg=None
        )

        self.assertTrue(self.account.db.accessibility_preferences["screenreader"])

    def test_charcreate_does_not_initialize_item_components_on_unsaved_character(self):
        """Characters must not inherit the physical-item component host."""

        self.assertFalse(issubclass(Character, ComponentHolderMixin))
        self.assertTrue(issubclass(PortableItem, ComponentHolderMixin))

        with patch(
            "evennia.contrib.rpg.character_creator.character_creator.EvMenu"
        ) as menu:
            result = self.call(
                ContribCmdCharCreate(), "", caller=self.account, msg=None
            )

        self.assertNotIn("Cannot add", result)
        menu.assert_called_once()

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
        with (
            patch.object(self.account, "execute_cmd") as execute,
            patch("commands.account_commands.reactor.callLater") as call_later,
        ):
            callback(self.account, "confirm", "yes")

        self.assertIsNone(self.char1.pk)
        call_later.assert_called_once_with(
            0, execute, "look", session=command.session
        )
