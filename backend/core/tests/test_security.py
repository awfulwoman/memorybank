from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Group, User


class NonMemberAccessBlockedTest(TestCase):
    """US-008: Verify non-member, non-staff users get 403 on group endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(username="admin", password="pass", is_staff=True)
        self.alice = User.objects.create_user(username="alice", password="pass")
        self.bob = User.objects.create_user(username="bob", password="pass")
        self.group = Group.objects.create(name="G", created_by=self.staff)
        self.group.members.add(self.staff, self.alice)
        # bob is NOT a member

    def test_bob_get_expenses_403(self):
        self.client.force_login(self.bob)
        resp = self.client.get(f"/api/groups/{self.group.pk}/expenses/")
        self.assertEqual(resp.status_code, 403)

    def test_bob_post_expenses_403(self):
        self.client.force_login(self.bob)
        resp = self.client.post(f"/api/groups/{self.group.pk}/expenses/", {
            "amount": "10.00",
            "description": "Test",
            "date": "2026-01-01",
        }, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_bob_get_settlements_403(self):
        self.client.force_login(self.bob)
        resp = self.client.get(f"/api/groups/{self.group.pk}/settlements/")
        self.assertEqual(resp.status_code, 403)

    def test_bob_post_settlements_403(self):
        self.client.force_login(self.bob)
        resp = self.client.post(f"/api/groups/{self.group.pk}/settlements/", {
            "payee": self.alice.pk,
            "amount": "10.00",
            "date": "2026-01-01",
        }, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_bob_get_balances_403(self):
        self.client.force_login(self.bob)
        resp = self.client.get(f"/api/groups/{self.group.pk}/balances/")
        self.assertEqual(resp.status_code, 403)

    def test_bob_get_export_403(self):
        self.client.force_login(self.bob)
        resp = self.client.get(f"/api/groups/{self.group.pk}/export/")
        self.assertEqual(resp.status_code, 403)

    def test_staff_nonmember_get_expenses_200(self):
        """Staff can access any group's expenses even if not a member."""
        staff2 = User.objects.create_user(username="staff2", password="pass", is_staff=True)
        # staff2 is NOT a member of the group
        self.client.force_login(staff2)
        resp = self.client.get(f"/api/groups/{self.group.pk}/expenses/")
        self.assertEqual(resp.status_code, 200)

    def test_member_get_expenses_200(self):
        """Group members can access their group's expenses."""
        self.client.force_login(self.alice)
        resp = self.client.get(f"/api/groups/{self.group.pk}/expenses/")
        self.assertEqual(resp.status_code, 200)


class InvalidPayeeAndSplitsTest(TestCase):
    """US-009: Verify invalid settlement payees and expense splits are rejected."""

    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(username="admin", password="pass", is_staff=True)
        self.alice = User.objects.create_user(username="alice", password="pass")
        self.outsider = User.objects.create_user(username="outsider", password="pass")
        self.group = Group.objects.create(name="G", created_by=self.staff)
        self.group.members.add(self.staff, self.alice)
        # outsider is NOT a member
        self.client.force_login(self.staff)

    def test_settlement_nonmember_payee_400(self):
        resp = self.client.post(f"/api/groups/{self.group.pk}/settlements/", {
            "payee": self.outsider.pk,
            "amount": "50.00",
            "date": "2026-01-15",
        }, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_expense_nonmember_split_400(self):
        resp = self.client.post(f"/api/groups/{self.group.pk}/expenses/", {
            "amount": "100.00",
            "description": "Test",
            "date": "2026-01-01",
            "split_data": [
                {"user_id": self.outsider.pk, "amount": "100.00"},
            ],
        }, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_settlement_valid_payee_201(self):
        resp = self.client.post(f"/api/groups/{self.group.pk}/settlements/", {
            "payee": self.alice.pk,
            "amount": "50.00",
            "date": "2026-01-15",
        }, format="json")
        self.assertEqual(resp.status_code, 201)

    def test_expense_valid_split_201(self):
        resp = self.client.post(f"/api/groups/{self.group.pk}/expenses/", {
            "amount": "100.00",
            "description": "Test",
            "date": "2026-01-01",
            "split_data": [
                {"user_id": self.staff.pk, "amount": "50.00"},
                {"user_id": self.alice.pk, "amount": "50.00"},
            ],
        }, format="json")
        self.assertEqual(resp.status_code, 201)
