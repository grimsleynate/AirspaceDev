"""Tests for Quasar's player-facing commands."""

from evennia import create_object
from evennia.server.models import ServerConfig
from evennia.utils.test_resources import EvenniaCommandTest

from unittest.mock import patch

from .player_commands import (
    CmdContainerSizes,
    CmdEquipment,
    CmdGreet,
    CmdInventory,
    CmdInnate,
    CmdMap,
    CmdNumpadLook,
    CmdNumpadNorth,
    CmdOxygen,
    CmdSkill,
    CmdSoundTest,
    CmdVitals,
)
from typeclasses.items import CONTAINER_SIZE_CONFIG
from typeclasses.items import PortableItem, UtilityPressureSuit
from typeclasses.npcs import FriendlyNPC, OrientationGuide
from world.character_options import apply_species


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
        suit = create_object(
            UtilityPressureSuit, key="pressure suit", location=self.char1
        )
        widget = create_object(PortableItem, key="widget", location=self.char1)
        self.assertTrue(suit.equip_to(self.char1, quiet=True))

        result = self.call(CmdInventory(), "", msg=None)

        self.assertIn("widget", result)
        self.assertIn("(1/8)", result)
        self.assertNotIn("pressure suit", result)


class TargetedInteractionCommandTests(EvenniaCommandTest):
    def test_social_alias_targets_npc_by_dbref(self):
        guide = create_object(FriendlyNPC, key="station guide", location=self.room1)

        with patch.object(guide, "at_greet") as at_greet:
            self.call(CmdGreet(), f"#{guide.id}", msg=None, cmdstring="nod")

        at_greet.assert_called_once_with(self.char1, session=self.session, social="nod")

    def test_greeting_dialogue_npc_opens_its_dialogue(self):
        guide = create_object(
            OrientationGuide, key="station guide", location=self.room1
        )

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
            "Unknown sound. Choose confirm, objective, door, terminal, hurt, attack, or scene.",
        )


class ResourceCommandTests(EvenniaCommandTest):
    def test_vitals_uses_the_character_career_resource(self):
        self.char1.db.species = "synth"
        self.char1.db.career = "technician"

        result = self.call(CmdVitals(), "", msg=None)

        self.assertIn("Health:", result)
        self.assertIn("Tech Points:", result)
        self.assertNotIn("Oxygen:", result)

    def test_synth_oxygen_command_explains_the_immunity(self):
        self.char1.db.species = "synth"

        self.call(CmdOxygen(), "", "Your synthetic body does not require oxygen.")


class SpeciesBenefitCommandTests(EvenniaCommandTest):
    def setUp(self):
        super().setUp()
        self.char1.location = self.room1

    def test_spectrum_reads_authored_clue(self):
        apply_species(self.char1, "nimri")
        self.room1.db.spectrum_desc = "A hidden ultraviolet route points east."
        result = self.call(CmdInnate(), "", msg=None, cmdstring="spectrum")
        self.assertIn("hidden ultraviolet route", result)

    def test_resonance_reads_authored_clue(self):
        apply_species(self.char1, "kaelith")
        self.room1.db.resonance_desc = "One support carries impossible strain."
        result = self.call(CmdInnate(), "", msg=None, cmdstring="resonate")
        self.assertIn("impossible strain", result)

    def test_presence_recognizes_friendly_npcs(self):
        apply_species(self.char1, "veyari")
        create_object(FriendlyNPC, key="wayhouse keeper", location=self.room1)
        result = self.call(CmdInnate(), "", msg=None, cmdstring="presence")
        self.assertIn("wayhouse keeper", result)

    def test_imprint_preserves_and_recalls_one_scene(self):
        apply_species(self.char1, "serev")
        self.room1.db.desc = "A room worth remembering."
        self.call(CmdInnate(), "", "You and your mantle commit", cmdstring="imprint")
        result = self.call(CmdInnate(), "recall", msg=None, cmdstring="imprint")
        self.assertIn("A room worth remembering", result)


class KeyboardCommandTests(EvenniaCommandTest):
    def test_equipment_has_short_eq_alias(self):
        self.assertIn("eq", CmdEquipment.aliases)

    def test_cast_has_requested_c_alias(self):
        self.assertEqual(CmdSkill.key, "cast")
        self.assertIn("c", CmdSkill.aliases)

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
