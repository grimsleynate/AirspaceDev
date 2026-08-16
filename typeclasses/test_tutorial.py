"""Integration tests for the private distress-satellite tutorial."""

from unittest.mock import patch

from evennia.utils.test_resources import EvenniaTest

from typeclasses.tutorial import PersonalPortablePorter, TutorialRoom
from world import tutorial
from world.tutorial_data import ROOMS


class PrivateTutorialTests(EvenniaTest):
    def setUp(self):
        super().setUp()
        for character in (self.char1, self.char2):
            character.db.tutorial_complete = False
            character.attributes.remove("tutorial_instance_id")
            character.attributes.remove("tutorial_progress")
            character.attributes.remove("morality_events")
            character.attributes.remove("morality_score")

    def _build(self, character):
        return tutorial.create_tutorial_instance(character, enter=True)

    def _move(self, character, role):
        room = tutorial.role_room(character, role)
        character.move_to(room, quiet=True, move_type="teleport")
        return room

    def _carry(self, character, role):
        item = tutorial.role_object(character, role)
        item.move_to(character, quiet=True)
        tutorial.handle_item_collected(character, item)
        return item

    def test_two_characters_share_topology_but_keep_private_story_layers(self):
        first = self._build(self.char1)
        second = self._build(self.char2)
        shared_rooms = [
            obj for obj in tutorial.shared_objects() if isinstance(obj, TutorialRoom)
        ]

        self.assertEqual(len(shared_rooms), len(ROOMS))
        self.assertEqual(first, second)
        self.assertTrue(first.db.tutorial_shared)
        self.assertNotEqual(self.char1.db.tutorial_instance_id, self.char2.db.tutorial_instance_id)
        self.assertEqual(first.db.map_area_id, second.db.map_area_id)
        self.assertFalse(
            any(isinstance(obj, TutorialRoom) for obj in tutorial.instance_objects(self.char1))
        )
        self.assertLessEqual(len(tutorial.instance_objects(self.char1)), 6)
        self.assertNotEqual(
            self.char1.db.tutorial_identifier_fragments,
            self.char2.db.tutorial_identifier_fragments,
        )
        feeder = tutorial.role_object(self.char1, "corpse_feeder")
        self.assertFalse(feeder.access(self.char2, "view"))
        self.assertEqual(tutorial.ensure_tutorial_instance(self.char1), first)

    def test_shared_room_hides_players_and_actor_messages(self):
        room = self._build(self.char1)
        self._build(self.char2)
        self.char2.move_to(room, quiet=True, move_type="teleport")

        self.assertEqual(self.char1.location, self.char2.location)
        self.assertEqual(room.get_display_characters(self.char1), "")
        self.assertFalse(self.char2.access(self.char1, "view"))
        with patch.object(self.char1, "msg") as first_message, patch.object(
            self.char2, "msg"
        ) as second_message:
            room.msg_contents("private movement", from_obj=self.char1)

        self.assertTrue(first_message.called)
        self.assertFalse(second_message.called)

    def test_all_rooms_are_gravity_stable_and_only_command_starts_breathable(self):
        self._build(self.char1)
        rooms = [obj for obj in tutorial.shared_objects() if isinstance(obj, TutorialRoom)]

        self.assertTrue(all(room.db.gravity for room in rooms))
        breathable = {room.db.tutorial_role for room in rooms if room.db.atmosphere == "breathable"}
        self.assertEqual(breathable, {"command_center"})

    def test_airlock_cycles_without_venting_command(self):
        self._build(self.char1)
        lock = tutorial.role_room(self.char1, "command_pressure_lock")
        command = tutorial.role_room(self.char1, "command_center")
        lift = tutorial.role_room(self.char1, "command_deck_lift")

        self.assertTrue(tutorial.cycle_airlock_for_exit(self.char1, lock, lift, lock))
        self.assertEqual(lock.atmosphere_for(self.char1), "vacuum")
        self.assertTrue(tutorial.cycle_airlock_for_exit(self.char1, lock, lock, command))
        self.assertEqual(lock.atmosphere_for(self.char1), "breathable")
        self.assertEqual(command.atmosphere_for(self.char1), "breathable")

    def test_airlock_and_command_atmosphere_are_private_per_character(self):
        self._build(self.char1)
        self._build(self.char2)
        lock = tutorial.role_room(self.char1, "command_pressure_lock")
        command = tutorial.role_room(self.char1, "command_center")

        tutorial.save_progress(
            self.char1,
            pressure_lock_atmosphere="breathable",
            command_decompressed=True,
        )

        self.assertEqual(lock.atmosphere_for(self.char1), "vacuum")
        self.assertEqual(command.atmosphere_for(self.char1), "vacuum")
        self.assertEqual(lock.atmosphere_for(self.char2), "vacuum")
        self.assertEqual(command.atmosphere_for(self.char2), "breathable")

    def test_full_rescue_playthrough_reaches_touch_porter_completion(self):
        self._build(self.char1)
        tutorial.save_progress(
            self.char1,
            corpse_feeder_defeated=True,
            survivors_contacted=True,
            met_survivors=True,
            stores_code=True,
        )

        self._move(self.char1, "emergency_stores")
        self.assertTrue(tutorial.open_stores_cabinet(self.char1))
        self._carry(self.char1, "induction_bridge")

        knot = tutorial.role_object(self.char1, "feeding_knot")
        tutorial.handle_tutorial_hostile_defeat(knot)
        wafer = self._carry(self.char1, "routing_wafer")
        self._move(self.char1, "navigation_control")
        self.assertTrue(tutorial.calibrate_wafer(self.char1))
        self.assertTrue(wafer.db.calibrated)

        tutorial.save_progress(self.char1, overtaken_raider_defeated=True)
        self._move(self.char1, "auxiliary_power_core")
        self.assertTrue(tutorial.install_bridge(self.char1))
        self.assertTrue(tutorial.activate_power(self.char1))

        self._move(self.char1, "emergency_transit_chamber")
        self.assertTrue(tutorial.recover_porter(self.char1))
        self.assertTrue(tutorial.bind_porter(self.char1))
        self.assertTrue(tutorial.install_wafer(self.char1))
        self.assertTrue(tutorial.test_transit(self.char1))

        self._move(self.char1, "command_center")
        juno = tutorial.role_object(self.char1, "overtaken_juno")
        self.assertIsNotNone(juno)
        tutorial.handle_juno_bite(juno, self.char1)
        tutorial.handle_tutorial_hostile_defeat(juno)
        self.assertTrue(tutorial.choose_mara_fate(self.char1, "rescue"))

        porter = tutorial.role_object(self.char1, "porter")
        self.assertEqual(self.char1.location.db.tutorial_role, "command_center")
        self.assertFalse(porter.db.equipped)
        self.assertTrue(tutorial.porter_conversation(self.char1, topic="status"))
        self.assertTrue(tutorial.touch_porter(self.char1))
        self.assertTrue(self.char1.db.tutorial_complete)
        self.assertEqual(self.char1.location.key, "Hexcom Receiver Facility (Under Construction)")
        self.assertTrue(self.char1.db.rescued_mara_venn)
        self.assertTrue(self.char1.db.mara_infection_unresolved)
        self.assertEqual(self.char1.db.morality_score, 1)
        self.assertEqual(tutorial.instance_objects(self.char1), [])
        porter = next(obj for obj in self.char1.contents if isinstance(obj, PersonalPortablePorter))
        self.assertEqual(tutorial.role_object(self.char1, "porter"), porter)
        self.assertTrue(tutorial.porter_conversation(self.char1, topic="status"))
        self.assertFalse(tutorial.touch_porter(self.char1))

    def test_early_unaware_departure_is_neutral(self):
        self._build(self.char1)
        self._move(self.char1, "emergency_transit_chamber")
        tutorial.recover_porter(self.char1)
        tutorial.bind_porter(self.char1)
        self._move(self.char1, "navigation_control")

        self.assertTrue(tutorial.touch_porter(self.char1))
        self.assertIn("tutorial_porter_departure:unaware", self.char1.db.morality_events)
        self.assertEqual(self.char1.db.morality_score, 0)
        self.assertFalse(bool(self.char1.db.rescued_mara_venn))

    def test_recovering_porter_prompts_binding_without_requiring_equipment(self):
        self._build(self.char1)
        self._move(self.char1, "emergency_transit_chamber")

        with patch.object(self.char1, "msg") as message:
            self.assertTrue(tutorial.recover_porter(self.char1))

        output = "\n".join(str(call.args[0]) for call in message.call_args_list if call.args)
        porter = tutorial.role_object(self.char1, "porter")
        self.assertIn("BIND PORTER", output)
        self.assertFalse(porter.db.equipped)
        self.assertTrue(porter.db.cosmetic_equipment)
        self.assertEqual(porter.combat_stat_summary(), "")
        self.assertTrue(tutorial.bind_porter(self.char1))
        self.assertTrue(tutorial.porter_conversation(self.char1, topic="status"))

    def test_porter_transport_expires_after_level_ten_but_conversation_does_not(self):
        self._build(self.char1)
        self._move(self.char1, "emergency_transit_chamber")
        tutorial.recover_porter(self.char1)
        tutorial.bind_porter(self.char1)
        self.char1.db.level = 11

        self.assertFalse(tutorial.has_porter_transport_access(self.char1))
        self.assertFalse(tutorial.touch_porter(self.char1))
        self.assertTrue(tutorial.porter_conversation(self.char1, topic="status"))

        self.char1.db.hexcom_porter_subscription_active = True
        self.assertTrue(tutorial.has_porter_transport_access(self.char1))
        self.assertTrue(tutorial.porter_conversation(self.char1, topic="status"))

    def test_level_ten_still_has_complimentary_porter_transport(self):
        self._build(self.char1)
        self.char1.db.level = 10

        self.assertTrue(tutorial.has_porter_transport_access(self.char1))

    def test_airlock_sabotage_kills_survivors_awards_xp_and_cancels_tasks(self):
        self._build(self.char1)
        from world.resources import initialize_character

        initialize_character(self.char1, include_starter_gear=True)
        self._move(self.char1, "command_pressure_lock")
        before_xp = int(self.char1.db.experience or 0)

        self.assertTrue(tutorial.cut_airlock_door(self.char1, "east"))
        self.assertFalse(tutorial.progress(self.char1).get("command_decompressed", False))
        self.assertTrue(tutorial.cut_airlock_door(self.char1, "north"))

        state = tutorial.progress(self.char1)
        self.assertTrue(state["command_decompressed"])
        self.assertTrue(state["survivor_tasks_cancelled"])
        self.assertTrue(state["juno_defeated"])
        self.assertIsNone(tutorial.role_object(self.char1, "mara"))
        self.assertIsNone(tutorial.role_object(self.char1, "juno"))
        self.assertEqual(
            tutorial.role_room(self.char1, "command_center").atmosphere_for(self.char1),
            "vacuum",
        )
        self.assertEqual(int(self.char1.db.experience), before_xp + 100)
        self.assertEqual(self.char1.db.morality_score, -2)

    def test_hostile_defeat_changes_room_prose_and_spawns_wafer(self):
        self._build(self.char1)
        reception = tutorial.role_room(self.char1, "shattered_reception")
        feeder = tutorial.role_object(self.char1, "corpse_feeder")
        self.assertIn("Something pale", tutorial.room_description(reception, self.char1))

        tutorial.handle_tutorial_hostile_defeat(feeder)
        self.assertIn("Dark feeding membranes", tutorial.room_description(reception, self.char1))

        knot = tutorial.role_object(self.char1, "feeding_knot")
        tutorial.handle_tutorial_hostile_defeat(knot)
        self.assertIsNotNone(tutorial.role_object(self.char1, "routing_wafer"))

    def test_feeding_parasites_do_not_start_combat_on_room_entry(self):
        self._build(self.char1)
        feeder = tutorial.role_object(self.char1, "corpse_feeder")
        # Simulate a persisted instance from before passive feeding behavior.
        feeder.db.aggressive = True

        self._move(self.char1, "shattered_reception")

        self.assertFalse(feeder.db.aggressive)
        self.assertIsNone(self.char1.db.combat_target_id)
        self.assertIsNone(feeder.db.combat_target_id)

    @patch("world.combat.resolve_attack", return_value={"hit": True, "critical": False, "damage": 1})
    def test_attacking_a_feeding_parasite_starts_automatic_combat(self, _resolve):
        self._build(self.char1)
        feeder = tutorial.role_object(self.char1, "corpse_feeder")
        self._move(self.char1, "shattered_reception")
        from world.combat import player_attack

        player_attack(self.char1, feeder, now=100.0)

        self.assertEqual(self.char1.db.combat_target_id, feeder.id)
        self.assertEqual(feeder.db.combat_target_id, self.char1.id)

    def test_juno_mutation_scene_forces_the_final_fight(self):
        self._build(self.char1)
        tutorial.save_progress(
            self.char1,
            survivors_contacted=True,
            met_survivors=True,
            companion_transit_ready=True,
        )

        self._move(self.char1, "command_center")
        hostile = tutorial.role_object(self.char1, "overtaken_juno")

        self.assertIsNotNone(hostile)
        self.assertTrue(hostile.db.aggressive)
        self.assertEqual(self.char1.db.combat_target_id, hostile.id)
        self.assertEqual(hostile.db.combat_target_id, self.char1.id)

    def test_deleting_character_deletes_unfinished_instance(self):
        self._build(self.char1)
        instance_id = str(self.char1.db.tutorial_instance_id)
        shared_room_ids = {obj.id for obj in tutorial.shared_objects() if isinstance(obj, TutorialRoom)}

        self.char1.delete()

        self.assertEqual(list(tutorial.search_tag(instance_id, category=tutorial.INSTANCE_CATEGORY)), [])
        self.assertEqual(
            {obj.id for obj in tutorial.shared_objects() if isinstance(obj, TutorialRoom)},
            shared_room_ids,
        )
