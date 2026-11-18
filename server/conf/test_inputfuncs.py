"""Tests for Quasar's OOB input functions (GMCP / MSDP / webclient)."""

from unittest import TestCase
from unittest.mock import Mock, patch

from server.conf import inputfuncs


class QuasarInputFuncTests(TestCase):
    @patch("world.resources.send_character_resources")
    def test_character_request_sends_resource_snapshot(self, send_resources):
        session = Mock(puppet=Mock())

        inputfuncs.quasar_character_get(session)

        send_resources.assert_called_once_with(
            session.puppet, session=session, force=True
        )

    @patch("world.room_effects.send_room_effects")
    def test_room_effect_support_is_negotiated_and_synced(self, send_room_effects):
        session = Mock(puppet=Mock())

        inputfuncs.quasar_room_effects_supports(session, version=1)

        session.update_flags.assert_called_once_with(QUASAR_ROOM_EFFECTS=True)
        send_room_effects.assert_called_once_with(
            session.puppet, session=session, force=True
        )

    @patch("world.audio.send_audio_scene")
    def test_audio_support_is_negotiated_and_synced(self, send_audio_scene):
        session = Mock(puppet=Mock())

        inputfuncs.quasar_audio_supports(session, version=1)

        session.update_flags.assert_called_once_with(QUASAR_AUDIO=True)
        send_audio_scene.assert_called_once_with(
            session.puppet, session=session, force=True
        )

    @patch("world.accessibility.apply_accessibility_preferences")
    def test_accessibility_request_applies_account_preferences(self, apply_preferences):
        session = Mock(account=Mock(), puppet=Mock())

        inputfuncs.quasar_accessibility_get(session)

        session.update_flags.assert_called_once_with(QUASAR_ACCESSIBILITY=True)
        apply_preferences.assert_called_once_with(
            session.account, session=session, character=session.puppet
        )

    @patch("world.accessibility.apply_accessibility_preferences")
    def test_accessibility_support_is_remembered_before_login(self, apply_preferences):
        session = Mock(account=None, puppet=None)

        inputfuncs.quasar_accessibility_get(session)

        session.update_flags.assert_called_once_with(QUASAR_ACCESSIBILITY=True)
        apply_preferences.assert_not_called()
