"""Structural coverage for authored character-option help."""

from unittest import TestCase

from world.character_options import ABILITY_TREES, BACKGROUNDS, SPECIES
from world.help_character_options import HELP_ENTRY_DICTS
from world.help_character_options import get_option_help


class CharacterOptionHelpTests(TestCase):
    def test_every_option_has_a_dedicated_help_entry(self):
        self.assertEqual(len(HELP_ENTRY_DICTS), 3 + len(SPECIES) + len(BACKGROUNDS) + len(ABILITY_TREES))
        by_key = {entry["key"].lower(): entry for entry in HELP_ENTRY_DICTS}
        for catalog in (SPECIES, BACKGROUNDS, ABILITY_TREES):
            for option in catalog.values():
                with self.subTest(option=option["name"]):
                    self.assertIn(option["name"].lower(), by_key)
                    self.assertIn("\n\n", by_key[option["name"].lower()]["text"])

    def test_ability_help_lists_titles_without_ability_descriptions(self):
        by_key = {entry["key"].lower(): entry for entry in HELP_ENTRY_DICTS}
        for tree in ABILITY_TREES.values():
            text = by_key[tree["name"].lower()]["text"]
            self.assertIn("Unlockable abilities:", text)
            for title in tree["abilities"]:
                self.assertIn(f"  - {title}", text)

    def test_chargen_lookup_reuses_global_help_text(self):
        by_key = {entry["key"].lower(): entry for entry in HELP_ENTRY_DICTS}
        self.assertEqual(get_option_help("species", "oruun"), by_key["oruun"]["text"])
        self.assertEqual(get_option_help("background", "heimdall_rigger"), by_key["heimdall rigger"]["text"])
        self.assertEqual(get_option_help("ability_tree", "ballistics"), by_key["ballistics"]["text"])
