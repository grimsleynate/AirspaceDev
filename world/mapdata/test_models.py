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
        self.room1.db.map_area = "Test Station"
        self.room1.db.map_x = 0
        self.room1.db.map_y = 0
        self.room1.db.map_z = 0
        self.room2.db.map_area = "Other Station"
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

    def test_sync_uses_quasar_gmcp_output(self):
        with patch.object(self.char1, "msg") as mocked_msg:
            send_map_sync(self.char1)

        payload = mocked_msg.call_args.kwargs["quasar_map_sync"]
        self.assertEqual(payload["character"]["id"], self.char1.id)
