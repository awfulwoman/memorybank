from django.test import TestCase
from rest_framework.test import APIClient

from core.models import User


class MeViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="pass", display_name="Test"
        )
        self.client.force_login(self.user)

    def test_get_me(self):
        resp = self.client.get("/api/users/me/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["display_name"], "Test")

    def test_patch_display_name(self):
        resp = self.client.patch(
            "/api/users/me/", {"display_name": "Updated"}, format="json"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["display_name"], "Updated")

    def test_avatar_no_file_returns_400(self):
        resp = self.client.post("/api/users/me/avatar/")
        self.assertEqual(resp.status_code, 400)
