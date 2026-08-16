"""Tests for Quasar's native-client audio protocol."""

from unittest.mock import Mock, patch

from evennia.utils.test_resources import EvenniaTest

from world.audio import build_audio_scene, emit_audio, send_audio_scene


class AudioProtocolTests(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.char1.location = self.room1
        self.room1.db.audio_scene = "test.station"
        self.room1.db.audio_music = "music.quasar_drift"
        self.room1.db.audio_ambience = [
            {"event": "ambience.station_air", "gain": 0.6},
            "not a valid event",
        ]
        self.room1.db.audio_fade_ms = 2500

    def test_room_scene_uses_semantic_catalog_ids(self):
        payload = build_audio_scene(self.room1)

        self.assertEqual(payload["scene"], "test.station")
        self.assertEqual(payload["music"], "music.quasar_drift")
        self.assertEqual(
            payload["ambience"],
            [{"event": "ambience.station_air", "gain": 0.6}],
        )
        self.assertEqual(payload["fade_ms"], 2500)

    def test_existing_tutorial_rooms_receive_deck_scene_before_batch_upgrade(self):
        self.room1.attributes.remove("audio_scene")
        self.room1.attributes.remove("audio_music")
        self.room1.attributes.remove("audio_ambience")
        self.room1.db.map_area = "Quasar Orientation Annex"
        self.room1.db.map_z = -1

        payload = build_audio_scene(self.room1)

        self.assertEqual(payload["scene"], "tutorial.engineering_deck")
        self.assertEqual(payload["music"], "music.quasar_drift")
        self.assertEqual(len(payload["ambience"]), 2)

    def test_duplicate_scene_is_not_resent_to_same_session(self):
        session = Mock(protocol_flags={"QUASAR_AUDIO": 1})

        send_audio_scene(self.char1, session=session)
        send_audio_scene(self.char1, session=session)

        session.msg.assert_called_once_with(
            quasar_audio_scene=build_audio_scene(self.room1)
        )

    @patch("world.audio._supported_sessions")
    def test_one_shot_event_only_targets_supported_sessions(self, sessions):
        session = Mock()
        sessions.return_value = [session]

        payload = emit_audio(
            self.char1,
            "combat.player_hurt",
            gain=0.8,
            priority=70,
        )

        session.msg.assert_called_once_with(quasar_audio_play=payload)
        self.assertEqual(payload["event"], "combat.player_hurt")
        self.assertNotIn("url", payload)

    def test_invalid_event_id_is_rejected(self):
        with self.assertRaises(ValueError):
            emit_audio(self.char1, "https://example.com/unsafe.mp3")
