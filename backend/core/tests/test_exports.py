import json

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from core.models import Expense, ExpenseSplit, Group, User


@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'core.authentication.ApiKeyAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'URL_FORMAT_OVERRIDE': None,
})
class ExportAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.u1 = User.objects.create_user(username="u1", password="pass", is_staff=True)
        self.u2 = User.objects.create_user(username="u2", password="pass")
        self.group = Group.objects.create(name="G", created_by=self.u1)
        self.group.members.add(self.u1, self.u2)
        self.client.force_login(self.u1)
        # Create an expense
        exp = Expense.objects.create(
            amount="100.00", description="Test", date="2026-01-01",
            group=self.group, created_by=self.u1,
        )
        ExpenseSplit.objects.create(expense=exp, user=self.u1, amount="50.00")
        ExpenseSplit.objects.create(expense=exp, user=self.u2, amount="50.00")

    def test_group_export_csv(self):
        resp = self.client.get(f"/api/groups/{self.group.pk}/export/?format=csv")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/csv", resp["Content-Type"])
        content = resp.content.decode()
        self.assertIn("description", content.lower())

    def test_group_export_json(self):
        resp = self.client.get(f"/api/groups/{self.group.pk}/export/?format=json")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("application/json", resp["Content-Type"])
        data = json.loads(resp.content)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_group_export_xml_returns_400(self):
        resp = self.client.get(f"/api/groups/{self.group.pk}/export/?format=xml")
        self.assertEqual(resp.status_code, 400)

    def test_me_export_csv_own_expenses_only(self):
        # u2 creates an expense
        self.client.force_login(self.u2)
        Expense.objects.create(
            amount="30.00", description="U2Expense", date="2026-01-02",
            group=self.group, created_by=self.u2,
        )
        # u1 export should not include u2's expense
        self.client.force_login(self.u1)
        resp = self.client.get("/api/users/me/export/?format=csv")
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertIn("Test", content)
        self.assertNotIn("U2Expense", content)
