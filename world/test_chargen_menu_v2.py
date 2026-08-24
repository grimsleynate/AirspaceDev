"""Tests for the launch people/background/tree character creator."""

from evennia.utils.test_resources import EvenniaTest

from world import chargen_menu
from world.character_options import ABILITY_TREES, ARCHETYPES, BACKGROUNDS, MINISKILLS, SPECIES


class LaunchChargenTests(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.caller = self.char1
        self.caller.new_char = self.char2

    @staticmethod
    def displayed_keys(options):
        return [option["key"][0] for option in options if str(option["key"][0]).isdigit()]

    def test_welcome_offers_archetype_and_free_creation(self):
        _text, options = chargen_menu.menunode_welcome(self.caller)
        self.assertEqual(self.displayed_keys(options), ["1", "2", "3"])

    def test_accessibility_is_configurable_inside_chargen(self):
        text, options = chargen_menu.menunode_accessibility(self.caller)

        self.assertIn("Screen reader", text)
        self.assertEqual(self.displayed_keys(options), ["1", "2", "3", "4", "5"])
        node = chargen_menu._set_accessibility_menu(
            self.caller, "", setting="screenreader"
        )
        self.assertEqual(node, "menunode_accessibility")
        self.assertTrue(self.caller.account.db.accessibility_preferences["screenreader"])
        self.assertFalse(self.caller.account.db.accessibility_preferences["room_effects"])

    def test_six_biological_peoples_and_no_synth(self):
        text, options = chargen_menu.menunode_species(self.caller)
        self.assertEqual(len(SPECIES), 6)
        self.assertNotIn("synth", SPECIES)
        self.assertEqual(self.displayed_keys(options), ["1", "2", "3", "4", "5", "6"])
        self.assertIn("help <species>", text)
        self.assertTrue(any(option["key"] == "_default" for option in options))

    def test_option_help_is_readable_before_committing_a_choice(self):
        node, kwargs = chargen_menu._menu_help_dispatch(
            self.caller,
            "help Oruun",
            catalog_kind="species",
            return_node="menunode_species",
        )
        self.assertEqual(node, "menunode_option_help")
        text, options = chargen_menu.menunode_option_help(self.caller, **kwargs)
        self.assertIn("lightless oceans", text)
        self.assertIn("Raking Bite", text)
        self.assertEqual(options[0]["goto"], "menunode_species")

        node, kwargs = chargen_menu._menu_help_dispatch(
            self.caller,
            "help Ballistics",
            catalog_kind="ability_tree",
            return_node="menunode_tree_one",
        )
        text, _options = chargen_menu.menunode_option_help(self.caller, **kwargs)
        self.assertIn("Unlockable abilities:", text)
        self.assertIn("Terminal Solution", text)

    def test_twelve_backgrounds_and_eight_basic_trees(self):
        self.assertEqual(len(BACKGROUNDS), 12)
        self.assertEqual(len(ABILITY_TREES), 8)

    def test_archetype_prefills_editable_independent_fields(self):
        next_node = chargen_menu._set_archetype(self.caller, "", archetype_key="abyssal_surveyor")
        character = self.caller.new_char
        self.assertEqual(next_node, "menunode_species")
        self.assertEqual(character.db.species, "oruun")
        self.assertEqual(character.db.background, "belt_prospector")
        self.assertEqual(character.db.basic_trees, ["delving", "channeling"])
        self.assertEqual(character.db.active_skill_trees, ["delving", "channeling"])
        self.assertEqual(character.db.skill_tree_proficiency, {"delving": 1, "channeling": 1})
        self.assertEqual(character.db.background_miniskill, "claim_assay")
        self.assertEqual(character.db.unlocked_miniskills, ["claim_assay"])
        self.assertEqual(character.db.species_benefit, "raking_bite")
        self.assertFalse(character.db.background_knack)
        self.assertFalse(character.db.heritage)

    def test_every_people_appears_twice_in_archetypes(self):
        counts = {key: 0 for key in SPECIES}
        for archetype in ARCHETYPES.values():
            counts[archetype["species"]] += 1
        self.assertEqual(set(counts.values()), {2})

    def test_second_tree_cannot_duplicate_first(self):
        self.caller.new_char.db.basic_trees = ["ballistics", None]
        _text, options = chargen_menu.menunode_tree_two(self.caller)
        self.assertTrue(any(option["key"] == "_default" for option in options))
        first_numbered = next(option for option in options if option["key"][0] == "1")
        self.assertEqual(first_numbered["goto"][1], {"tree_key": "breachwork"})
        surprise = next(option for option in options if option["key"][0] == "s")
        self.assertEqual(surprise["goto"][1]["component"], "tree_two_key")
        self.assertEqual(options[-1]["goto"], "menunode_tree_one")
        self.assertEqual(
            chargen_menu._set_tree_two(self.caller, "", tree_key="ballistics"),
            "menunode_tree_two",
        )
        self.assertEqual(
            chargen_menu._set_tree_two(self.caller, "", tree_key="warding"),
            "menunode_name",
        )
        self.assertEqual(self.caller.new_char.db.active_skill_trees, ["ballistics", "warding"])

    def test_numbered_tree_one_option_passes_the_setter_argument(self):
        _text, options = chargen_menu.menunode_tree_one(self.caller)
        first_numbered = next(option for option in options if option["key"][0] == "1")
        setter, kwargs = first_numbered["goto"]
        self.assertIs(setter, chargen_menu._set_tree_one)
        self.assertEqual(kwargs, {"tree_key": "ballistics"})
        self.assertEqual(setter(self.caller, "1", **kwargs), "menunode_tree_two")

    def test_human_and_native_opening_defaults_are_distinct(self):
        chargen_menu._set_species(self.caller, "", species_key="human")
        human = self.caller.new_char.db.opening_premise
        self.caller.new_char.db.opening_premise = None
        chargen_menu._set_species(self.caller, "", species_key="oruun")
        native = self.caller.new_char.db.opening_premise
        self.assertNotEqual(human, native)
        self.assertIn("Dawnline", human)
        self.assertIn("Dawnline", native)

    def test_archetype_and_custom_paths_converge_after_name_at_final_review(self):
        character = self.caller.new_char
        chargen_menu._begin_path(self.caller, "", path="archetype")
        self.assertEqual(
            chargen_menu._set_archetype(
                self.caller, "", archetype_key="frontier_gunner"
            ),
            "menunode_species",
        )
        chargen_menu._set_species(self.caller, "", species_key="oruun")
        self.assertEqual(
            chargen_menu._set_gender(self.caller, "", gender_key="neutral"),
            "menunode_name",
        )
        self.assertEqual(
            chargen_menu._validate_name(self.caller, "ArchetypeTester"),
            "menunode_review",
        )
        self.assertTrue(character.db.chargen_name_selected)

        character.db.chargen_editing = False
        character.db.chargen_path = "custom"
        character.db.basic_trees = ["ballistics"]
        self.assertEqual(
            chargen_menu._set_tree_two(self.caller, "", tree_key="warding"),
            "menunode_name",
        )

    def test_editing_first_tree_updates_the_active_build(self):
        chargen_menu._set_archetype(self.caller, "", archetype_key="frontier_gunner")
        self.caller.new_char.db.chargen_editing = True
        self.assertEqual(chargen_menu._set_tree_one(self.caller, "", tree_key="biotech"), "menunode_review")
        self.assertEqual(self.caller.new_char.db.basic_trees, ["biotech", "breachwork"])
        self.assertEqual(self.caller.new_char.db.active_skill_trees, ["biotech", "breachwork"])
        self.assertEqual(self.caller.new_char.db.known_skill_trees, ["biotech", "breachwork"])
        self.assertEqual(set(self.caller.new_char.db.skill_tree_proficiency), {"biotech", "breachwork"})

    def test_background_grants_exactly_one_miniskill_then_moves_to_ability_trees(self):
        self.assertEqual(
            chargen_menu._set_background(self.caller, "", background_key="political_operator"),
            "menunode_tree_one",
        )
        self.assertEqual(self.caller.new_char.db.background_miniskill, "coalition_barter")
        self.assertEqual(self.caller.new_char.db.unlocked_miniskills, ["coalition_barter"])
        self.assertIn("shop_price_multiplier", MINISKILLS["coalition_barter"]["effects"])

        chargen_menu._set_background(self.caller, "", background_key="wayhouse_raised")
        self.assertEqual(self.caller.new_char.db.unlocked_miniskills, ["wayhouse_cant"])

    def test_each_nonhuman_body_receives_its_own_portrait_and_chassis(self):
        expected_chassis = {
            "oruun": "aquatic_dense",
            "nimri": "bipedal",
            "serev": "symbiotic",
            "kaelith": "radial",
            "veyari": "tripodal",
        }
        for species, chassis in expected_chassis.items():
            with self.subTest(species=species):
                chargen_menu._set_species(self.caller, "", species_key=species)
                chargen_menu._set_gender(
                    self.caller, "", gender_key="neutral"
                )
                self.assertEqual(
                    self.caller.new_char.db.locomotion_chassis, chassis
                )
                self.assertEqual(
                    self.caller.new_char.db.portrait_id,
                    f"{species}_neutral",
                )
                self.assertIn(
                    f"{species}-neutral.png",
                    self.caller.new_char.db.portrait_url,
                )

    def test_final_review_contains_name_and_is_only_finalize_gateway(self):
        chargen_menu._begin_path(self.caller, "", path="archetype")
        chargen_menu._set_archetype(
            self.caller, "", archetype_key="frontier_gunner"
        )
        chargen_menu._set_species(self.caller, "", species_key="human")
        chargen_menu._set_gender(self.caller, "", gender_key="neutral")
        chargen_menu._validate_name(self.caller, "FinalTester")

        text, options = chargen_menu.menunode_review(self.caller)

        self.assertIn("FinalTester", text)
        self.assertEqual(len(options), 9)
        self.assertEqual(options[0]["goto"], "menunode_confirm")
        self.assertEqual(options[1]["goto"], "menunode_name")
        self.assertNotIn("Heritage", text)
        self.assertNotIn("Obligation", text)

    def test_species_benefits_are_varied_and_bounded(self):
        kinds = {entry["benefit"]["kind"] for entry in SPECIES.values()}
        self.assertEqual(kinds, {"practice", "natural_weapon", "command"})
        self.assertEqual(SPECIES["oruun"]["benefit"]["unarmed_damage_bonus"], 1)
        self.assertLessEqual(SPECIES["human"]["benefit"]["starting_practice"], 5)

    def test_interrupted_old_completion_returns_to_review_and_clears_flag(self):
        character = self.caller.new_char
        chargen_menu.apply_archetype(character, "frontier_gunner")
        character.db.gender = "neutral"
        character.db.chargen_complete = True
        character.db.chargen_name_selected = False

        text, _options = chargen_menu.menunode_confirm(self.caller)

        self.assertIn("Final Review", text)
        self.assertFalse(character.db.chargen_complete)
        self.assertEqual(character.db.chargen_step, "menunode_review")
