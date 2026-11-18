"""Tests for trusted room-effect resolution and native-client sync."""

from unittest.mock import Mock, patch

from evennia.utils.test_resources import EvenniaTest

from world.audio import build_audio_scene
from world.room_effects import ROOM_EFFECTS, build_room_effects, send_room_effects

# Fixture registry: one night-only visual, one night-only audio layer, and one
# always-on effect with both. Real effects are registered in ROOM_EFFECTS.
TEST_EFFECTS = {
    "test.night_visual": {
        "periods": {"night"},
        "visual": {"preset": "night_insects", "intensity": 0.5},
    },
    "test.night_audio": {
        "periods": {"night"},
        "audio": [{"event": "ambience.test_night", "gain": 0.3}],
    },
    "test.always": {
        "visual": {"preset": "electric_flicker", "intensity": 0.4},
        "audio": [{"event": "ambience.test_always", "gain": 0.2}],
    },
}


@patch.dict(ROOM_EFFECTS, TEST_EFFECTS, clear=True)
class RoomEffectsTests(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.char1.location = self.room1
        self.room1.db.room_effect_ids = [
            "test.night_visual",
            "test.night_audio",
            "unknown.database_payload",
            "test.always",
        ]

    def test_only_registered_visual_effects_are_serialized(self):
        self.room1.db.room_effect_period = "night"

        payload = build_room_effects(self.room1)

        self.assertEqual(
            [effect["id"] for effect in payload["effects"]],
            ["test.night_visual", "test.always"],
        )
        self.assertNotIn("audio", payload["effects"][0])

    def test_malformed_builder_effect_data_fails_closed(self):
        self.room1.db.room_effect_ids = 42

        payload = build_room_effects(self.room1)

        self.assertEqual(payload["effects"], [])

    def test_night_only_effects_are_filtered_during_day(self):
        self.room1.db.room_effect_period = "day"

        payload = build_room_effects(self.room1)

        self.assertEqual([effect["id"] for effect in payload["effects"]], ["test.always"])

    def test_room_effects_contribute_semantic_audio_layers(self):
        self.room1.db.room_effect_period = "night"

        events = [layer["event"] for layer in build_audio_scene(self.room1)["ambience"]]

        self.assertEqual(events, ["ambience.test_night", "ambience.test_always"])

    def test_duplicate_scene_is_not_resent(self):
        self.room1.db.room_effect_period = "night"
        session = Mock(protocol_flags={"BENBEN_ROOM_EFFECTS": 1})

        send_room_effects(self.char1, session=session)
        send_room_effects(self.char1, session=session)

        session.msg.assert_called_once_with(
            benben_room_effects_sync=build_room_effects(self.room1)
        )
