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


class SettlementBalanceTest(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username="u1", password="pass")
        self.u2 = User.objects.create_user(username="u2", password="pass")
        self.group = Group.objects.create(name="G")
        self.group.members.add(self.u1, self.u2)
        # u1 pays 100, split equally => u2 owes u1 50
        self.exp = Expense.objects.create(
            amount=Decimal("100.00"),
            description="Dinner",
            date="2026-01-01",
            group=self.group,
            created_by=self.u1,
        )
        ExpenseSplit.objects.create(expense=self.exp, user=self.u1, amount=Decimal("50.00"))
        ExpenseSplit.objects.create(expense=self.exp, user=self.u2, amount=Decimal("50.00"))

    def _get_balances(self):
        expenses = Expense.objects.filter(group=self.group).select_related("created_by").prefetch_related("splits__user")
        settlements = Settlement.objects.filter(group=self.group).select_related("payer", "payee")
        return _compute_balances(expenses, settlements)

    def test_partial_settlement_reduces_debt(self):
        Settlement.objects.create(
            group=self.group, payer=self.u2, payee=self.u1,
            amount=Decimal("20.00"), date="2026-01-02",
        )
        net, pairwise = self._get_balances()
        self.assertEqual(len(pairwise), 1)
        debt = pairwise[0]
        self.assertEqual(debt["amount"], Decimal("30.00"))

    def test_full_settlement_zeros_debt(self):
        Settlement.objects.create(
            group=self.group, payer=self.u2, payee=self.u1,
            amount=Decimal("50.00"), date="2026-01-02",
        )
        net, pairwise = self._get_balances()
        self.assertEqual(pairwise, [])
        self.assertEqual(dict(net), {})


class MultiMemberBalanceTest(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username="u1", password="pass")
        self.u2 = User.objects.create_user(username="u2", password="pass")
        self.u3 = User.objects.create_user(username="u3", password="pass")
        self.group = Group.objects.create(name="G")
        self.group.members.add(self.u1, self.u2, self.u3)

    def _get_balances(self):
        expenses = Expense.objects.filter(group=self.group).select_related("created_by").prefetch_related("splits__user")
        settlements = Settlement.objects.filter(group=self.group).select_related("payer", "payee")
        return _compute_balances(expenses, settlements)

    def test_multiple_payers_net_balances(self):
        # u1 pays 90, split 30 each
        exp1 = Expense.objects.create(
            amount=Decimal("90.00"), description="E1", date="2026-01-01",
            group=self.group, created_by=self.u1,
        )
        for u in [self.u1, self.u2, self.u3]:
            ExpenseSplit.objects.create(expense=exp1, user=u, amount=Decimal("30.00"))

        # u2 pays 60, split 20 each
        exp2 = Expense.objects.create(
            amount=Decimal("60.00"), description="E2", date="2026-01-01",
            group=self.group, created_by=self.u2,
        )
        for u in [self.u1, self.u2, self.u3]:
            ExpenseSplit.objects.create(expense=exp2, user=u, amount=Decimal("20.00"))

        net, pairwise = self._get_balances()
        # u1 net: owed 30+30=60 from E1, owes 20 from E2 = +40
        # u3 net: owes 30 to u1, owes 20 to u2 = -50
        self.assertEqual(net[self.u1.pk], Decimal("40.00"))
        self.assertEqual(net[self.u3.pk], Decimal("-50.00"))

    def test_three_members_cross_debts_simplify(self):
        # u1 pays 60, split 20 each => u2 owes u1 20, u3 owes u1 20
        exp1 = Expense.objects.create(
            amount=Decimal("60.00"), description="E1", date="2026-01-01",
            group=self.group, created_by=self.u1,
        )
        for u in [self.u1, self.u2, self.u3]:
            ExpenseSplit.objects.create(expense=exp1, user=u, amount=Decimal("20.00"))

        # u2 pays 30, split 10 each => u1 owes u2 10, u3 owes u2 10
        exp2 = Expense.objects.create(
            amount=Decimal("30.00"), description="E2", date="2026-01-01",
            group=self.group, created_by=self.u2,
        )
        for u in [self.u1, self.u2, self.u3]:
            ExpenseSplit.objects.create(expense=exp2, user=u, amount=Decimal("10.00"))

        net, pairwise = self._get_balances()
        # After netting: u2->u1 net 10, u3->u1 20, u3->u2 10
        self.assertEqual(net[self.u1.pk], Decimal("30.00"))
        self.assertEqual(net[self.u3.pk], Decimal("-30.00"))
