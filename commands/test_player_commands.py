"""Tests for player-facing commands."""

from evennia import create_object
from evennia.server.models import ServerConfig
from evennia.utils.test_resources import EvenniaCommandTest

from unittest.mock import patch

from .player_commands import (
    CmdContainerSizes,
    CmdEquipment,
    CmdGreet,
    CmdInventory,
    CmdMap,
    CmdNumpadLook,
    CmdNumpadNorth,
    CmdSoundTest,
    CmdVitals,
)
from typeclasses.items import CONTAINER_SIZE_CONFIG
from typeclasses.items import EquipableItem, PortableItem
from typeclasses.npcs import FriendlyNPC


class DialogueNPC(FriendlyNPC):
    """Test fixture: a friendly NPC that hosts an EvMenu dialogue."""

    dialogue_module = "commands.test_player_commands"


class ContainerSizeAdminCommandTests(EvenniaCommandTest):
    def tearDown(self):
        ServerConfig.objects.conf(CONTAINER_SIZE_CONFIG, delete=True)
        super().tearDown()

    def test_admin_can_toggle_size_checks(self):
        self.char1.permissions.add("Admin")

        self.call(
            CmdContainerSizes(),
            "off",
            "Container size system is OFF: item dimensions are ignored; count capacities still apply.",
        )
        self.assertFalse(ServerConfig.objects.conf(CONTAINER_SIZE_CONFIG))
        self.call(
            CmdContainerSizes(),
            "on",
            "Container size system is ON: items must fit the container's interior dimensions.",
        )
        self.assertTrue(ServerConfig.objects.conf(CONTAINER_SIZE_CONFIG))


class InventoryCommandTests(EvenniaCommandTest):
    def test_inventory_hides_equipped_items_and_reports_slot_usage(self):
        suit = create_object(EquipableItem, key="test armor", location=self.char1)
        widget = create_object(PortableItem, key="widget", location=self.char1)
        self.assertTrue(suit.equip_to(self.char1, quiet=True))

        result = self.call(CmdInventory(), "", msg=None)

        self.assertIn("widget", result)
        self.assertIn("(1/8)", result)
        self.assertNotIn("test armor", result)


class TargetedInteractionCommandTests(EvenniaCommandTest):
    def test_social_alias_targets_npc_by_dbref(self):
        guide = create_object(FriendlyNPC, key="guide", location=self.room1)

        with patch.object(guide, "at_greet") as at_greet:
            self.call(CmdGreet(), f"#{guide.id}", msg=None, cmdstring="nod")

        at_greet.assert_called_once_with(self.char1, session=self.session, social="nod")

    def test_greeting_dialogue_npc_opens_its_dialogue(self):
        guide = create_object(DialogueNPC, key="guide", location=self.room1)

        with patch.object(guide, "at_talk") as at_talk:
            guide.at_greet(self.char1, session="test-session", social="wave")

        at_talk.assert_called_once_with(self.char1, session="test-session")

    def test_social_alias_can_target_another_player(self):
        self.char2.location = self.room1

        result = self.call(CmdGreet(), f"#{self.char2.id}", msg=None, cmdstring="wave")

        self.assertIn("wave", result)


class MapCommandTests(EvenniaCommandTest):
    def test_screenreader_profile_blocks_map_display_and_reenable(self):
        from world.accessibility import set_accessibility_preferences

        set_accessibility_preferences(self.account, screenreader=True)

        result = self.call(CmdMap(), "", msg=None)
        self.assertIn("ASCII maps are disabled", result)
        result = self.call(CmdMap(), "on", msg=None)
        self.assertIn("ASCII maps are disabled", result)

    def test_map_on_is_case_insensitive(self):
        self.call(CmdMap(), "ON", "ASCII map enabled.")
        self.assertTrue(self.char1.db.ascii_map_enabled)

    def test_map_off_is_case_insensitive(self):
        self.call(CmdMap(), "oFf", "ASCII map disabled.")
        self.assertFalse(self.char1.db.ascii_map_enabled)

    def test_map_without_argument_displays_current_map(self):
        result = self.call(CmdMap(), "", msg=None)
        self.assertIn("[@]", result)

    def test_map_rejects_unknown_option(self):
        self.call(CmdMap(), "sometimes", "Usage: map, map on, map off, or map reset")

    def test_map_reset_requires_confirmation(self):
        self.call(
            CmdMap(),
            "reset",
            "This will permanently forget this character's explored map. Use map reset confirm to continue.",
        )


class SoundTestCommandTests(EvenniaCommandTest):
    @patch("world.audio.emit_audio")
    def test_named_test_sound_emits_semantic_event(self, emit_audio):
        self.call(CmdSoundTest(), "hurt", "Audio event sent: combat.player_hurt")

        emit_audio.assert_called_once_with(self.char1, "combat.player_hurt")

    def test_unknown_test_sound_lists_choices(self):
        self.call(
            CmdSoundTest(),
            "banana",
            "Unknown sound. Choose confirm, objective, door, hurt, attack, or scene.",
        )


class ResourceCommandTests(EvenniaCommandTest):
    def test_vitals_reports_health_and_level(self):
        result = self.call(CmdVitals(), "", msg=None)

        self.assertIn("Health:", result)
        self.assertIn("Level:", result)


class KeyboardCommandTests(EvenniaCommandTest):
    def test_equipment_has_short_eq_alias(self):
        self.assertIn("eq", CmdEquipment.aliases)

    def test_numeric_keypad_commands_translate_to_standard_commands(self):
        with patch.object(self.char1, "execute_cmd") as execute:
            north = CmdNumpadNorth()
            north.caller = self.char1
            north.session = None
            north.func()
            look = CmdNumpadLook()
            look.caller = self.char1
            look.session = None
            look.func()

        self.assertEqual(execute.call_args_list[0].args[0], "north")
        self.assertEqual(execute.call_args_list[1].args[0], "look")
