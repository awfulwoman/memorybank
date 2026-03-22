from django.test import TestCase
from rest_framework.test import APIClient

from core.models import ApiKey, User


class LoginLogoutTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="pass123")

    def test_login_valid_credentials(self):
        resp = self.client.post("/api/auth/login/", {"username": "testuser", "password": "pass123"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["username"], "testuser")

    def test_login_invalid_credentials(self):
        resp = self.client.post("/api/auth/login/", {"username": "testuser", "password": "wrong"})
        self.assertEqual(resp.status_code, 401)

    def test_logout(self):
        self.client.force_login(self.user)
        resp = self.client.post("/api/auth/logout/")
        self.assertEqual(resp.status_code, 200)

    def test_unauthenticated_me_returns_401_or_403(self):
        resp = self.client.get("/api/users/me/")
        self.assertIn(resp.status_code, [401, 403])


class ApiKeyAuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="pass123")

    def test_create_api_key(self):
        self.client.force_login(self.user)
        resp = self.client.post("/api/users/me/api-key/")
        self.assertEqual(resp.status_code, 201)
        self.assertIn("key", resp.json())

    def test_create_api_key_replaces_old(self):
        self.client.force_login(self.user)
        resp1 = self.client.post("/api/users/me/api-key/")
        key1 = resp1.json()["key"]
        resp2 = self.client.post("/api/users/me/api-key/")
        key2 = resp2.json()["key"]
        self.assertNotEqual(key1, key2)
        self.assertEqual(ApiKey.objects.filter(user=self.user).count(), 1)

    def test_delete_api_key(self):
        self.client.force_login(self.user)
        self.client.post("/api/users/me/api-key/")
        resp = self.client.delete("/api/users/me/api-key/")
        self.assertEqual(resp.status_code, 204)

    def test_delete_api_key_when_none_returns_404(self):
        self.client.force_login(self.user)
        resp = self.client.delete("/api/users/me/api-key/")
        self.assertEqual(resp.status_code, 404)

    def test_api_key_authenticates(self):
        self.client.force_login(self.user)
        resp = self.client.post("/api/users/me/api-key/")
        key = resp.json()["key"]
        self.client.logout()
        # Use API key header
        resp = self.client.get("/api/users/me/", HTTP_X_API_KEY=key)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["username"], "testuser")
