from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Group, User


class SettlementAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(username="admin", password="pass", is_staff=True)
        self.alice = User.objects.create_user(username="alice", password="pass")
        self.group = Group.objects.create(name="G", created_by=self.staff)
        self.group.members.add(self.staff, self.alice)
        self.client.force_login(self.staff)

    def test_create_settlement(self):
        resp = self.client.post(f"/api/groups/{self.group.pk}/settlements/", {
            "payee": self.alice.pk,
            "amount": "50.00",
            "date": "2026-01-15",
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["payer"], self.staff.pk)
        self.assertEqual(resp.json()["payee"], self.alice.pk)

    def test_list_settlements(self):
        self.client.post(f"/api/groups/{self.group.pk}/settlements/", {
            "payee": self.alice.pk,
            "amount": "25.00",
            "date": "2026-01-15",
        }, format="json")
        resp = self.client.get(f"/api/groups/{self.group.pk}/settlements/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
