"""Tests for persistent accessibility preferences and media suppression."""

from unittest.mock import Mock

from evennia.utils.test_resources import EvenniaTest

from world.accessibility import (
    apply_accessibility_preferences,
    get_accessibility_preferences,
    set_accessibility_preferences,
)
from world.audio import build_audio_scene, send_audio_scene
from world.room_effects import build_room_effects, send_room_effects


class AccessibilityTests(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.account.characters.add(self.char1)
        self.char1.location = self.room1
        self.room1.db.room_effect_period = "night"
        self.room1.db.room_effect_ids = ["wayhouse.electric_lamps"]

    def test_screenreader_profile_forces_color_maps_and_media_off(self):
        preferences = set_accessibility_preferences(
            self.account,
            screenreader=True,
            color_mode="truecolor",
            room_effects=True,
            ascii_maps=True,
        )

        self.assertTrue(preferences["screenreader"])
        self.assertEqual(preferences["color_mode"], "off")
        self.assertFalse(preferences["room_effects"])
        self.assertFalse(preferences["ascii_maps"])

    def test_preferences_apply_to_transport_and_persist(self):
        set_accessibility_preferences(self.account, screenreader=True)
        session = Mock(
            protocol_flags={"QUASAR_ACCESSIBILITY": 1}, sessionhandler=Mock()
        )

        apply_accessibility_preferences(
            self.account, session=session, character=self.char1
        )

        self.assertTrue(session.protocol_flags["SCREENREADER"])
        self.assertTrue(session.protocol_flags["NOCOLOR"])
        self.assertFalse(self.char1.db.ascii_map_enabled)
        self.assertTrue(self.account.db._saved_protocol_flags["SCREENREADER"])
        session.msg.assert_called_once()

    def test_prelogin_screenreader_flag_is_adopted_for_new_account_preference(self):
        self.account.attributes.remove("accessibility_preferences")
        session = Mock(
            protocol_flags={"SCREENREADER": True}, sessionhandler=Mock()
        )

        apply_accessibility_preferences(self.account, session=session)

        preferences = get_accessibility_preferences(self.account)
        self.assertTrue(preferences["screenreader"])
        self.assertFalse(preferences["room_effects"])

    def test_screenreader_session_receives_silence_and_no_visual_effects(self):
        session = Mock(
            protocol_flags={
                "QUASAR_AUDIO": 1,
                "QUASAR_ROOM_EFFECTS": 1,
                "SCREENREADER": True,
            }
        )

        send_audio_scene(self.char1, session=session, force=True)
        send_room_effects(self.char1, session=session, force=True)

        self.assertEqual(
            session.msg.call_args_list[0].kwargs["quasar_audio_scene"],
            build_audio_scene(None),
        )
        self.assertEqual(
            session.msg.call_args_list[1].kwargs["quasar_room_effects_sync"],
            build_room_effects(None),
        )

    def test_individual_preferences_remain_available_without_screenreader(self):
        preferences = set_accessibility_preferences(
            self.account, screenreader=False, color_mode="ansi", room_effects=False
        )

        self.assertFalse(preferences["screenreader"])
        self.assertEqual(preferences["color_mode"], "ansi")
        self.assertFalse(preferences["room_effects"])
        self.assertTrue(get_accessibility_preferences(self.account)["ascii_maps"])

    def test_color_auto_restores_negotiated_capabilities_after_off(self):
        session = Mock(
            protocol_flags={
                "ANSI": True,
                "XTERM256": True,
                "TRUECOLOR": True,
            },
            sessionhandler=Mock(),
        )
        set_accessibility_preferences(self.account, color_mode="off")
        apply_accessibility_preferences(self.account, session=session)
        self.assertFalse(session.protocol_flags["ANSI"])

        set_accessibility_preferences(self.account, color_mode="auto")
        apply_accessibility_preferences(self.account, session=session)

        self.assertTrue(session.protocol_flags["ANSI"])
        self.assertTrue(session.protocol_flags["XTERM256"])
        self.assertTrue(session.protocol_flags["TRUECOLOR"])
        self.assertNotIn("ANSI", self.account.db._saved_protocol_flags)

    def test_color_auto_after_reconnect_uses_new_transport_capabilities(self):
        first_session = Mock(
            protocol_flags={
                "ANSI": True,
                "XTERM256": True,
                "TRUECOLOR": True,
            },
            sessionhandler=Mock(),
        )
        set_accessibility_preferences(self.account, color_mode="off")
        apply_accessibility_preferences(self.account, session=first_session)

        saved = dict(self.account.db._saved_protocol_flags)
        self.assertTrue(saved["NOCOLOR"])
        self.assertNotIn("ANSI", saved)
        self.assertNotIn("XTERM256", saved)
        self.assertNotIn("TRUECOLOR", saved)

        # Model Evennia restoring only the deliberately persistent flags onto
        # a freshly negotiated truecolor connection before post-login apply.
        second_flags = {
            "ANSI": True,
            "XTERM256": True,
            "TRUECOLOR": True,
            **saved,
        }
        second_session = Mock(protocol_flags=second_flags, sessionhandler=Mock())
        apply_accessibility_preferences(self.account, session=second_session)
        self.assertFalse(second_session.protocol_flags["ANSI"])

        set_accessibility_preferences(self.account, color_mode="auto")
        apply_accessibility_preferences(self.account, session=second_session)

        self.assertTrue(second_session.protocol_flags["ANSI"])
        self.assertTrue(second_session.protocol_flags["XTERM256"])
        self.assertTrue(second_session.protocol_flags["TRUECOLOR"])
