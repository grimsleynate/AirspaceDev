"""Routing tests for Benben's browser clients."""

from django.test import TestCase


class WebclientViewTests(TestCase):
    def test_react_client_is_default(self):
        response = self.client.get("/webclient/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="benben-root"')
        self.assertContains(response, "benben-client.js")
        self.assertNotContains(response, 'id="messagewindow"')

    def test_legacy_client_remains_available(self):
        response = self.client.get("/webclient/legacy/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="messagewindow"')
