"""Tests for server-backed character exploration."""

from unittest.mock import patch

from evennia.utils.test_resources import EvenniaTest

from world.mapdata.models import CharacterMapVisit
from world.mapping import (
    build_map_sync,
    clear_character_map,
    explored_room_ids,
    record_room_visit,
    send_map_sync,
)


class CharacterMapVisitTests(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.char1.location = self.room1
        self.room1.db.map_area = "Test Area"
        self.room1.db.map_x = 0
        self.room1.db.map_y = 0
        self.room1.db.map_z = 0
        self.room2.db.map_area = "Other Area"
        CharacterMapVisit.objects.filter(character_id=self.char1.id).delete()
        self.char1.ndb.explored_room_ids = None

    def test_only_first_visit_writes_a_row(self):
        self.assertTrue(record_room_visit(self.char1, self.room1))
        self.assertFalse(record_room_visit(self.char1, self.room1))
        self.assertEqual(
            CharacterMapVisit.objects.filter(character_id=self.char1.id).count(), 1
        )

    def test_map_sync_is_character_scoped_and_current_area_only(self):
        record_room_visit(self.char1, self.room1)
        record_room_visit(self.char1, self.room2)

        payload = build_map_sync(self.char1)

        self.assertEqual(payload["character"]["id"], self.char1.id)
        self.assertEqual(payload["current"], self.room1.id)
        self.assertEqual([room["num"] for room in payload["rooms"]], [self.room1.id])

    def test_reset_keeps_only_current_room(self):
        record_room_visit(self.char1, self.room1)
        record_room_visit(self.char1, self.room2)

        clear_character_map(self.char1, keep_current=True)

        self.assertEqual(explored_room_ids(self.char1), {self.room1.id})

    def test_sync_uses_benben_gmcp_output(self):
        with patch.object(self.char1, "msg") as mocked_msg:
            send_map_sync(self.char1)

        payload = mocked_msg.call_args.kwargs["benben_map_sync"]
        self.assertEqual(payload["character"]["id"], self.char1.id)


class AreaIdentityTests(EvenniaTest):
    """Repair plan step 6: discovery on arrival; area_key groups the map."""

    def setUp(self):
        super().setUp()
        CharacterMapVisit.objects.filter(character_id=self.char1.id).delete()
        self.char1.ndb.explored_room_ids = None
        self.char1.location = self.room2

    def test_quiet_teleport_records_a_visit_without_a_look(self):
        self.char1.move_to(self.room1, quiet=True, move_type="teleport")

        self.assertIn(self.room1.id, explored_room_ids(self.char1, refresh=True))

    def test_npc_arrival_records_nothing(self):
        from evennia import create_object
        from typeclasses.npcs import FriendlyNPC

        npc = create_object(FriendlyNPC, key="Wanderer", location=self.room2)
        npc.move_to(self.room1, quiet=True)

        self.assertFalse(CharacterMapVisit.objects.filter(character_id=npc.id).exists())

    def test_map_groups_by_area_key_not_display_name(self):
        # Same key, different display names and coordinate systems (a cave
        # under the vale): still one area.
        self.room1.db.area_key = "starting_vale"
        self.room1.db.map_area = "Starting Vale"
        self.room1.db.map_area_id = 1
        self.room2.db.area_key = "starting_vale"
        self.room2.db.map_area = "Vale Caverns"
        self.room2.db.map_area_id = 2
        record_room_visit(self.char1, self.room1)
        record_room_visit(self.char1, self.room2)
        self.char1.location = self.room1

        payload = build_map_sync(self.char1)

        self.assertEqual(payload["area_key"], "starting_vale")
        self.assertEqual(payload["area"], "Starting Vale")
        self.assertEqual(
            sorted(room["num"] for room in payload["rooms"]),
            sorted([self.room1.id, self.room2.id]),
        )
        self.assertEqual(payload["rooms"][0]["area_key"], "starting_vale")

    def test_unset_area_falls_back_to_uncharted(self):
        self.room1.attributes.remove("area_key")
        self.room1.attributes.remove("map_area")

        self.assertEqual(self.room1.area_key, "uncharted")
        self.assertEqual(self.room1.area_name, "Uncharted")
