"""Tests for trusted room-effect resolution and native-client sync."""

from unittest.mock import Mock

from evennia.utils.test_resources import EvenniaTest

from world.audio import build_audio_scene
from world.room_effects import build_room_effects, send_room_effects


class RoomEffectsTests(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.char1.location = self.room1
        self.room1.db.room_effect_ids = [
            "wayhouse.frontier_night",
            "wayhouse.low_wind",
            "unknown.database_payload",
            "wayhouse.electric_lamps",
            "wayhouse.night_insects",
        ]

    def test_only_registered_effects_are_serialized(self):
        self.room1.db.room_effect_period = "night"

        payload = build_room_effects(self.room1)

        self.assertEqual(
            [effect["id"] for effect in payload["effects"]],
            [
                "wayhouse.frontier_night",
                "wayhouse.electric_lamps",
                "wayhouse.night_insects",
            ],
        )
        self.assertNotIn("audio", payload["effects"][0])

    def test_malformed_builder_effect_data_fails_closed(self):
        self.room1.db.room_effect_ids = 42

        payload = build_room_effects(self.room1)

        self.assertEqual(payload["effects"], [])

    def test_night_only_effects_are_filtered_during_day(self):
        self.room1.db.room_effect_period = "day"

        payload = build_room_effects(self.room1)

        self.assertEqual(
            [effect["id"] for effect in payload["effects"]],
            ["wayhouse.electric_lamps"],
        )

    def test_room_effects_contribute_semantic_audio_layers(self):
        self.room1.db.room_effect_period = "night"

        events = [layer["event"] for layer in build_audio_scene(self.room1)["ambience"]]

        self.assertEqual(
            events,
            [
                "ambience.wayhouse_wind",
                "ambience.wayhouse_lamps",
                "ambience.wayhouse_insects",
            ],
        )

    def test_duplicate_scene_is_not_resent(self):
        self.room1.db.room_effect_period = "night"
        session = Mock(protocol_flags={"QUASAR_ROOM_EFFECTS": 1})

        send_room_effects(self.char1, session=session)
        send_room_effects(self.char1, session=session)

        session.msg.assert_called_once_with(
            quasar_room_effects_sync=build_room_effects(self.room1)
        )
