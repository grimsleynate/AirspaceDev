"""Tests for Quasar's player-facing commands."""

from evennia.utils.test_resources import EvenniaCommandTest

from unittest.mock import patch

from .player_commands import (
    CmdEquipment,
    CmdMap,
    CmdNumpadLook,
    CmdNumpadNorth,
    CmdOxygen,
    CmdSkill,
    CmdSoundTest,
    CmdVitals,
)


class MapCommandTests(EvenniaCommandTest):
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
