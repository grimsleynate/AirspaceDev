"""Tests for keyboard-friendly character-creation choices."""

from evennia.utils.test_resources import EvenniaTest

from world import chargen_menu


class NumericChargenChoiceTests(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.caller = self.char1
        self.caller.new_char = self.char2

    def _numeric_keys(self, options):
        return [next(key for key in option["key"] if str(key).isdigit()) for option in options]

    def _displayed_keys(self, options):
        return [option["key"][0] for option in options]

    def test_welcome_can_begin_with_one(self):
        _text, option = chargen_menu.menunode_welcome(self.caller)

        self.assertIn("1", option["key"])

    def test_species_background_and_career_include_numbered_back_option(self):
        for node in (
            chargen_menu.menunode_species,
            chargen_menu.menunode_background,
            chargen_menu.menunode_career,
        ):
            _text, options = node(self.caller)
            self.assertEqual(self._numeric_keys(options), ["1", "2", "3"])
            self.assertEqual(self._displayed_keys(options), ["1", "2", "3"])

    def test_specialization_and_review_are_fully_numbered(self):
        self.caller.new_char.db.species = "human"
        self.caller.new_char.db.background = "stationborn"
        self.caller.new_char.db.career = "vanguard"
        self.caller.new_char.db.specialization = "marine"
        self.caller.new_char.db.gender = "male"

        _text, specializations = chargen_menu.menunode_specialization(self.caller)
        _text, review = chargen_menu.menunode_review(self.caller)

        self.assertEqual(self._numeric_keys(specializations), ["1", "2", "3"])
        self.assertEqual(self._numeric_keys(review), ["1", "2", "3"])
        self.assertEqual(self._displayed_keys(specializations), ["1", "2", "3"])
        self.assertEqual(self._displayed_keys(review), ["1", "2", "3"])

    def test_human_gender_is_numbered_and_assigns_portrait(self):
        self.caller.new_char.db.species = "human"
        _text, options = chargen_menu.menunode_human_gender(self.caller)

        self.assertEqual(self._displayed_keys(options), ["1", "2", "3", "4"])
        chargen_menu._set_human_gender(self.caller, "1", gender_key="male")
        self.assertEqual(self.caller.new_char.db.gender, "male")
        self.assertEqual(self.caller.new_char.db.portrait_id, "human_male")

    def test_synth_records_only_origin_gender_and_uses_neutral_portrait(self):
        self.caller.new_char.db.species = "synth"

        next_node = chargen_menu._set_synth_origin_gender(
            self.caller, "2", gender_key="female"
        )

        self.assertEqual(next_node, "menunode_background")
        self.assertEqual(self.caller.new_char.db.pre_synth_gender, "female")
        self.assertIsNone(self.caller.new_char.db.gender)
        self.assertEqual(self.caller.new_char.db.portrait_id, "synth_neutral")

    def test_selecting_synth_installs_wheel_chassis(self):
        next_node = chargen_menu._set_species(self.caller, "2", species_key="synth")

        self.assertEqual(next_node, "menunode_synth_origin_gender")
        self.assertEqual(self.caller.new_char.db.locomotion_chassis, "wheel")
