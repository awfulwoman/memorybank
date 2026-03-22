from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Category, Currency, Group, GroupType, User


class AdminWritePermissionTest(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="admin", password="pass", is_staff=True)
        self.regular = User.objects.create_user(username="alice", password="pass", is_staff=False)
        self.client = APIClient()

    def test_non_staff_get_categories_200(self):
        self.client.force_login(self.regular)
        resp = self.client.get("/api/categories/")
        self.assertEqual(resp.status_code, 200)

    def test_non_staff_post_categories_403(self):
        self.client.force_login(self.regular)
        resp = self.client.post("/api/categories/", {"name": "Travel"})
        self.assertEqual(resp.status_code, 403)

    def test_staff_post_categories_201(self):
        self.client.force_login(self.staff)
        resp = self.client.post("/api/categories/", {"name": "Travel"})
        self.assertEqual(resp.status_code, 201)

    def test_staff_delete_categories_204(self):
        self.client.force_login(self.staff)
        cat = Category.objects.create(name="ToDelete")
        resp = self.client.delete(f"/api/categories/{cat.pk}/")
        self.assertEqual(resp.status_code, 204)

    def test_non_staff_post_groups_allowed(self):
        self.client.force_login(self.regular)
        cur = Currency.objects.create(name="USD", symbol="$", code="USD")
        gt = GroupType.objects.create(name="Home")
        resp = self.client.post("/api/groups/", {
            "name": "New Group",
            "currency": cur.pk,
            "group_type": gt.pk,
        })
        self.assertEqual(resp.status_code, 201)
