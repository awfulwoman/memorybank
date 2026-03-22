from decimal import Decimal

from django.test import TestCase

from core.models import Expense, ExpenseSplit, Group, Settlement, User
from core.views import _compute_balances


class BasicBalanceTest(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username="u1", password="pass")
        self.u2 = User.objects.create_user(username="u2", password="pass")
        self.group = Group.objects.create(name="G")
        self.group.members.add(self.u1, self.u2)

    def test_equal_split_two_members(self):
        """1 expense, 2 members, equal split — payer is owed half by other."""
        exp = Expense.objects.create(
            amount=Decimal("100.00"),
            description="Dinner",
            date="2026-01-01",
            group=self.group,
            created_by=self.u1,
        )
        ExpenseSplit.objects.create(expense=exp, user=self.u1, amount=Decimal("50.00"))
        ExpenseSplit.objects.create(expense=exp, user=self.u2, amount=Decimal("50.00"))

        expenses = Expense.objects.filter(group=self.group).select_related("created_by").prefetch_related("splits__user")
        net, pairwise = _compute_balances(expenses, [])

        # u2 owes u1 50
        self.assertEqual(len(pairwise), 1)
        debt = pairwise[0]
        self.assertEqual(debt["from_user_id"], self.u2.pk)
        self.assertEqual(debt["to_user_id"], self.u1.pk)
        self.assertEqual(debt["amount"], Decimal("50.00"))

    def test_no_expenses_returns_empty(self):
        """No expenses or settlements returns empty balances."""
        net, pairwise = _compute_balances([], [])
        self.assertEqual(dict(net), {})
        self.assertEqual(pairwise, [])

    def test_expense_with_no_creator_is_skipped(self):
        """Expense with created_by=None is skipped gracefully."""
        exp = Expense.all_objects.create(
            amount=Decimal("100.00"),
            description="Orphan",
            date="2026-01-01",
            group=self.group,
            created_by=None,
        )
        ExpenseSplit.objects.create(expense=exp, user=self.u1, amount=Decimal("50.00"))
        ExpenseSplit.objects.create(expense=exp, user=self.u2, amount=Decimal("50.00"))

        expenses = Expense.objects.filter(group=self.group).select_related("created_by").prefetch_related("splits__user")
        net, pairwise = _compute_balances(expenses, [])
        self.assertEqual(dict(net), {})
        self.assertEqual(pairwise, [])
