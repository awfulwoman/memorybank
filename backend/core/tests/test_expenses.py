from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Expense, Group, User


class ExpenseCRUDTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(username="admin", password="pass", is_staff=True)
        self.alice = User.objects.create_user(username="alice", password="pass")
        self.group = Group.objects.create(name="G", created_by=self.staff)
        self.group.members.add(self.staff, self.alice)

    def test_create_expense_equal_splits(self):
        self.client.force_login(self.staff)
        resp = self.client.post(f"/api/groups/{self.group.pk}/expenses/", {
            "amount": "100.00",
            "description": "Dinner",
            "date": "2026-01-01",
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(len(resp.json()["splits"]), 2)

    def test_create_expense_custom_splits(self):
        self.client.force_login(self.staff)
        resp = self.client.post(f"/api/groups/{self.group.pk}/expenses/", {
            "amount": "100.00",
            "description": "Dinner",
            "date": "2026-01-01",
            "split_data": [
                {"user_id": self.staff.pk, "amount": "70.00"},
                {"user_id": self.alice.pk, "amount": "30.00"},
            ],
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        splits = {s["user"]: s["amount"] for s in resp.json()["splits"]}
        self.assertEqual(splits[self.staff.pk], "70.00")
        self.assertEqual(splits[self.alice.pk], "30.00")

    def test_list_expenses_excludes_deleted(self):
        self.client.force_login(self.staff)
        # Create expense
        self.client.post(f"/api/groups/{self.group.pk}/expenses/", {
            "amount": "50.00", "description": "E1", "date": "2026-01-01",
        }, format="json")
        # Create and soft-delete another
        resp = self.client.post(f"/api/groups/{self.group.pk}/expenses/", {
            "amount": "30.00", "description": "E2", "date": "2026-01-01",
        }, format="json")
        exp_id = resp.json()["id"]
        self.client.delete(f"/api/expenses/{exp_id}/")

        resp = self.client.get(f"/api/groups/{self.group.pk}/expenses/")
        descs = [e["description"] for e in resp.json()]
        self.assertIn("E1", descs)
        self.assertNotIn("E2", descs)

    def test_patch_by_creator(self):
        self.client.force_login(self.staff)
        resp = self.client.post(f"/api/groups/{self.group.pk}/expenses/", {
            "amount": "50.00", "description": "Original", "date": "2026-01-01",
        }, format="json")
        exp_id = resp.json()["id"]
        resp = self.client.patch(f"/api/expenses/{exp_id}/", {
            "description": "Updated",
        }, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["description"], "Updated")

    def test_patch_by_non_creator_returns_403(self):
        self.client.force_login(self.staff)
        resp = self.client.post(f"/api/groups/{self.group.pk}/expenses/", {
            "amount": "50.00", "description": "E", "date": "2026-01-01",
        }, format="json")
        exp_id = resp.json()["id"]

        self.client.force_login(self.alice)
        resp = self.client.patch(f"/api/expenses/{exp_id}/", {
            "description": "Hacked",
        }, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_delete_soft_deletes(self):
        self.client.force_login(self.staff)
        resp = self.client.post(f"/api/groups/{self.group.pk}/expenses/", {
            "amount": "50.00", "description": "E", "date": "2026-01-01",
        }, format="json")
        exp_id = resp.json()["id"]
        resp = self.client.delete(f"/api/expenses/{exp_id}/")
        self.assertEqual(resp.status_code, 204)
        self.assertTrue(Expense.all_objects.get(pk=exp_id).is_deleted)

    def test_soft_deleted_not_in_list(self):
        self.client.force_login(self.staff)
        resp = self.client.post(f"/api/groups/{self.group.pk}/expenses/", {
            "amount": "50.00", "description": "Gone", "date": "2026-01-01",
        }, format="json")
        exp_id = resp.json()["id"]
        self.client.delete(f"/api/expenses/{exp_id}/")

        resp = self.client.get(f"/api/groups/{self.group.pk}/expenses/")
        ids = [e["id"] for e in resp.json()]
        self.assertNotIn(exp_id, ids)
