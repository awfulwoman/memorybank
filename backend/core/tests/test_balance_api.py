from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Expense, ExpenseSplit, Group, Settlement, User


class GroupBalanceAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.u1 = User.objects.create_user(username="u1", password="pass", is_staff=True)
        self.u2 = User.objects.create_user(username="u2", password="pass")
        self.group = Group.objects.create(name="G", created_by=self.u1)
        self.group.members.add(self.u1, self.u2)
        self.client.force_login(self.u1)

    def test_balances_after_expense_and_settlement(self):
        exp = Expense.objects.create(
            amount=Decimal("100.00"), description="D", date="2026-01-01",
            group=self.group, created_by=self.u1,
        )
        ExpenseSplit.objects.create(expense=exp, user=self.u1, amount=Decimal("50.00"))
        ExpenseSplit.objects.create(expense=exp, user=self.u2, amount=Decimal("50.00"))
        Settlement.objects.create(
            group=self.group, payer=self.u2, payee=self.u1,
            amount=Decimal("20.00"), date="2026-01-02",
        )

        resp = self.client.get(f"/api/groups/{self.group.pk}/balances/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # u2 still owes u1 30
        debts = data["debts"]
        self.assertEqual(len(debts), 1)
        self.assertEqual(Decimal(debts[0]["amount"]), Decimal("30.00"))

    def test_empty_group_returns_empty(self):
        resp = self.client.get(f"/api/groups/{self.group.pk}/balances/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["balances"], [])
        self.assertEqual(resp.json()["debts"], [])


class MeBalanceAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.u1 = User.objects.create_user(username="u1", password="pass", is_staff=True)
        self.u2 = User.objects.create_user(username="u2", password="pass")
        self.group = Group.objects.create(name="G", created_by=self.u1)
        self.group.members.add(self.u1, self.u2)
        self.client.force_login(self.u1)

    def test_me_balances_aggregate(self):
        exp = Expense.objects.create(
            amount=Decimal("80.00"), description="D", date="2026-01-01",
            group=self.group, created_by=self.u1,
        )
        ExpenseSplit.objects.create(expense=exp, user=self.u1, amount=Decimal("40.00"))
        ExpenseSplit.objects.create(expense=exp, user=self.u2, amount=Decimal("40.00"))

        resp = self.client.get("/api/users/me/balances/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # u1 is owed 40 total
        self.assertEqual(Decimal(data["total_balance"]), Decimal("40.00"))
