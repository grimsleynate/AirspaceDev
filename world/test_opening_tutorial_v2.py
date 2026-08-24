"""Integration tests for the two private launch tutorial shells."""

from evennia.utils.test_resources import EvenniaTest

from typeclasses.opening_tutorial import BoundPorter, OpeningHostile, OpeningRoom
from world.character_options import BACKGROUNDS, apply_background, apply_species
from world.opening_tutorial import _instance_objects, create_opening_tutorial, dream_description, finish_opening_tutorial, use_opening_interaction
from world.combat import find_active_skill, use_active_skill


class OpeningTutorialTests(EvenniaTest):
    def _prepare(self, character, species):
        apply_species(character, species)
        character.db.chargen_complete = True
        character.db.basic_trees = ["ballistics", "warding"]
        character.db.active_skill_trees = ["ballistics", "warding"]
        apply_background(character, "hullborn")
        character.db.opening_tutorial_complete = False
        character.db.tutorial_complete = False

    def test_human_shell_has_fourteen_rooms_stable_person_and_matching_skills(self):
        self._prepare(self.char1, "human")
        create_opening_tutorial(self.char1)
        rooms = [obj for obj in OpeningRoom.objects.all_family() if obj.db.tutorial_owner_id == self.char1.id]
        first = dream_description(self.char1)
        second = dream_description(self.char1)
        self.assertEqual(len(rooms), 14)
        self.assertEqual(first, second)
        self.assertIn("Ballistics and Warding", first)
        self.assertFalse(any(isinstance(obj, BoundPorter) for obj in self.char1.contents))
        hostiles = [obj for room in rooms for obj in room.contents if isinstance(obj, OpeningHostile)]
        self.assertTrue(hostiles)
        self.assertTrue(all(int(hostile.db.experience_reward or 0) == 0 for hostile in hostiles))

    def test_native_shell_has_twelve_rooms_and_begins_with_bound_porter(self):
        self._prepare(self.char1, "oruun")
        create_opening_tutorial(self.char1)
        rooms = [obj for obj in OpeningRoom.objects.all_family() if obj.db.tutorial_owner_id == self.char1.id]
        porter = next(obj for obj in self.char1.contents if isinstance(obj, BoundPorter))
        self.assertEqual(len(rooms), 12)
        self.assertTrue(porter.db.bound)
        self.assertEqual(porter.db.bound_to_id, self.char1.id)
        self.assertTrue(all(room.db.room_effect_period == "night" for room in rooms))
        self.assertTrue(
            all("wayhouse.electric_lamps" in room.db.room_effect_ids for room in rooms)
        )
        interiors = [room for room in rooms if room.db.tutorial_role == "guest_clinic"]
        exteriors = [room for room in rooms if room.db.tutorial_role == "shelter_yard"]
        self.assertNotIn("wayhouse.night_insects", interiors[0].db.room_effect_ids)
        self.assertIn("wayhouse.night_insects", exteriors[0].db.room_effect_ids)

    def test_lone_lamp_route_uses_only_east_and_west_not_relative_directions(self):
        self._prepare(self.char1, "oruun")
        create_opening_tutorial(self.char1)
        rooms = [
            obj
            for obj in OpeningRoom.objects.all_family()
            if obj.db.tutorial_owner_id == self.char1.id
        ]
        linear_exits = [
            exit_obj
            for room in rooms
            for exit_obj in room.exits
            if exit_obj.key not in {"return"}
        ]

        self.assertEqual({exit_obj.key for exit_obj in linear_exits}, {"east", "west"})
        forbidden = {"forward", "forwards", "back", "backward", "backwards", "f", "b"}
        self.assertFalse(
            any(
                forbidden.intersection(
                    {exit_obj.key.lower(), *(alias.lower() for alias in exit_obj.aliases.all())}
                )
                for exit_obj in linear_exits
            )
        )

    def test_native_tutorial_contains_authored_spectrum_and_resonance_clues(self):
        for character, species, attribute in (
            (self.char1, "nimri", "spectrum_desc"),
            (self.char2, "kaelith", "resonance_desc"),
        ):
            self._prepare(character, species)
            create_opening_tutorial(character)
            evidence = next(
                obj for obj in _instance_objects(character)
                if obj.key == "people's evidence"
            )
            self.assertTrue(evidence.attributes.get(attribute))

    def test_selected_basics_supply_two_real_starting_abilities(self):
        self._prepare(self.char1, "human")
        self.assertEqual(find_active_skill(self.char1, "sightline")["tree_key"], "ballistics")
        self.assertEqual(find_active_skill(self.char1, "reversal")["tree_key"], "warding")
        self.assertIsNone(find_active_skill(self.char1, "arc snare"))

    def test_real_cast_path_records_workshop_tree_proof(self):
        self._prepare(self.char1, "human")
        create_opening_tutorial(self.char1)
        workshop = next(room for room in OpeningRoom.objects.all_family() if room.db.tutorial_owner_id == self.char1.id and room.db.tutorial_role == "aux_workshop")
        target = next(obj for obj in workshop.contents if isinstance(obj, OpeningHostile) and obj.db.tutorial_practice_target)
        self.char1.location = workshop
        use_active_skill(self.char1, "sightline", hostile=target, now=100.0)
        self.assertIn("ballistics", self.char1.db.opening_tutorial_progress["combat_trees_used"])
        self.assertEqual(self.char1.db.tutorial_pending_skill_experience["ballistics"], 10)

    def test_both_shells_finish_in_private_dawnline_rooms_with_porter(self):
        for character, species in ((self.char1, "human"), (self.char2, "veyari")):
            self._prepare(character, species)
            create_opening_tutorial(character)
            destination = finish_opening_tutorial(character)
            self.assertEqual(character.location, destination)
            self.assertTrue(character.db.opening_tutorial_complete)
            self.assertTrue(any(isinstance(obj, BoundPorter) for obj in character.contents))
            self.assertIn("Dawnline", destination.db.map_area)
            self.assertTrue(character.db.porter_binding["bound"])

    def test_partial_instance_is_rebuilt_instead_of_accepted(self):
        self._prepare(self.char1, "human")
        start = create_opening_tutorial(self.char1)
        start.db.tutorial_role = "damaged_partial"
        self.char1.db.opening_tutorial_build_complete = False
        rebuilt = create_opening_tutorial(self.char1)
        rooms = [obj for obj in OpeningRoom.objects.all_family() if obj.db.tutorial_owner_id == self.char1.id]
        self.assertEqual(len(rooms), 14)
        self.assertEqual(rebuilt.db.tutorial_role, "contract_berth")

    def test_pending_practice_commits_exactly_once(self):
        self._prepare(self.char1, "human")
        create_opening_tutorial(self.char1)
        self.char1.db.skill_tree_experience = {}
        self.char1.db.tutorial_pending_skill_experience = {"ballistics": 20}
        finish_opening_tutorial(self.char1)
        finish_opening_tutorial(self.char1)
        self.assertEqual(self.char1.db.skill_tree_experience["ballistics"], 20)
        self.assertTrue(self.char1.db.tutorial_practice_committed)

    def test_missing_terminal_exit_forces_instance_repair(self):
        self._prepare(self.char1, "human")
        create_opening_tutorial(self.char1)
        broken = next(obj for obj in _instance_objects(self.char1) if obj.db.tutorial_role == "exit:observation_well:wake")
        old_id = broken.id
        broken.delete()
        create_opening_tutorial(self.char1)
        terminal = next(room for room in OpeningRoom.objects.all_family() if room.db.tutorial_owner_id == self.char1.id and room.db.tutorial_role == "observation_well")
        self.assertTrue(any(exit_obj.key == "wake" and exit_obj.id != old_id for exit_obj in terminal.exits))

    def test_all_backgrounds_produce_distinct_functional_expressions(self):
        self._prepare(self.char1, "human")
        create_opening_tutorial(self.char1)
        room = next(room for room in OpeningRoom.objects.all_family() if room.db.tutorial_owner_id == self.char1.id and room.db.tutorial_role == "manifest_office")
        self.char1.location = room
        expressions = set()
        for background_key in BACKGROUNDS:
            apply_background(self.char1, background_key)
            self.char1.db.opening_tutorial_progress = {}
            self.assertTrue(use_opening_interaction(self.char1, "miniskill on evidence"))
            expressions.add(self.char1.db.opening_tutorial_progress["background_expression"])
        self.assertEqual(len(expressions), 12)
