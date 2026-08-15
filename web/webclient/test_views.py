"""Routing tests for Quasar's browser clients."""

from django.test import TestCase


class WebclientViewTests(TestCase):
    def test_react_client_is_default(self):
        response = self.client.get("/webclient/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="quasar-root"')
        self.assertContains(response, "quasar-client.js")
        self.assertNotContains(response, 'id="messagewindow"')

    def test_legacy_client_remains_available(self):
        response = self.client.get("/webclient/legacy/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="messagewindow"')
