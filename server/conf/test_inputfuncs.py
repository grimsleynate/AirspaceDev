"""Tests for Quasar's websocket/GMCP input bridge."""

from unittest import TestCase
from unittest.mock import Mock, patch

from server.conf.inputfuncs import gmcp


class GmcpInputTests(TestCase):
    @patch("world.resources.send_character_resources")
    def test_character_request_dispatches_to_resource_snapshot(self, send_resources):
        character = Mock()
        session = Mock(puppet=character)

        gmcp(session, "Quasar.Character.Get", "")

        send_resources.assert_called_once_with(character, session=session, force=True)

    def test_unknown_package_is_ignored(self):
        session = Mock()

        gmcp(session, "Quasar.Unknown.Package", "")

    @patch("world.room_effects.send_room_effects")
    def test_room_effect_support_is_negotiated_and_synced(self, send_room_effects):
        session = Mock(protocol_flags={}, puppet=Mock())

        gmcp(session, "Quasar.Room_Effects.Supports", "")

        self.assertEqual(session.protocol_flags["QUASAR_ROOM_EFFECTS"], 1)
        send_room_effects.assert_called_once_with(
            session.puppet, session=session, force=True
        )

    @patch("world.accessibility.apply_accessibility_preferences")
    def test_accessibility_request_applies_account_preferences(self, apply_preferences):
        session = Mock(account=Mock(), puppet=Mock(), protocol_flags={})

        gmcp(session, "Quasar.Accessibility.Get", "")

        self.assertEqual(session.protocol_flags["QUASAR_ACCESSIBILITY"], 1)
        apply_preferences.assert_called_once_with(
            session.account, session=session, character=session.puppet
        )

    def test_accessibility_support_is_remembered_before_login(self):
        session = Mock(account=None, puppet=None, protocol_flags={})

        gmcp(session, "Quasar.Accessibility.Get", "")

        self.assertEqual(session.protocol_flags["QUASAR_ACCESSIBILITY"], 1)
