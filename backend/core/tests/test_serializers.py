from decimal import Decimal

from django.test import TestCase, RequestFactory

from core.models import Category, Currency, Group, GroupType, User
from core.serializers import (
    AdminUserSerializer, CategorySerializer, CurrencySerializer,
    ExpenseSerializer, GroupSerializer, GroupTypeSerializer,
    SettlementSerializer, UserSerializer,
)


class ExpenseSerializerEqualSplitTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="u1", password="pass")
        self.user2 = User.objects.create_user(username="u2", password="pass")
        self.group = Group.objects.create(name="G")
        self.group.members.add(self.user1, self.user2)

    def test_equal_splits_when_split_data_omitted(self):
        data = {
            "amount": "100.00",
            "description": "Dinner",
            "date": "2026-01-01",
        }
        serializer = ExpenseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        expense = serializer.save(created_by=self.user1, group=self.group)
        splits = expense.splits.all()
        self.assertEqual(splits.count(), 2)
        for s in splits:
            self.assertEqual(s.amount, Decimal("50.00"))

    def test_custom_splits_when_split_data_provided(self):
        data = {
            "amount": "100.00",
            "description": "Dinner",
            "date": "2026-01-01",
            "split_data": [
                {"user_id": self.user1.pk, "amount": "70.00"},
                {"user_id": self.user2.pk, "amount": "30.00"},
            ],
        }
        serializer = ExpenseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        expense = serializer.save(created_by=self.user1, group=self.group)
        splits = {s.user_id: s.amount for s in expense.splits.all()}
        self.assertEqual(splits[self.user1.pk], Decimal("70.00"))
        self.assertEqual(splits[self.user2.pk], Decimal("30.00"))

    def test_rejects_splits_not_summing_to_total(self):
        data = {
            "amount": "100.00",
            "description": "Dinner",
            "date": "2026-01-01",
            "split_data": [
                {"user_id": self.user1.pk, "amount": "60.00"},
                {"user_id": self.user2.pk, "amount": "30.00"},
            ],
        }
        serializer = ExpenseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        with self.assertRaises(Exception) as ctx:
            serializer.save(created_by=self.user1, group=self.group)
        self.assertIn("Sum of splits must equal expense amount", str(ctx.exception))


class AdminUserSerializerTest(TestCase):
    def test_create_hashes_password(self):
        data = {
            "username": "newuser",
            "password": "secret123",
            "display_name": "New",
        }
        serializer = AdminUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        self.assertTrue(user.check_password("secret123"))
        self.assertNotEqual(user.password, "secret123")

    def test_update_hashes_password(self):
        user = User.objects.create_user(username="existing", password="old")
        data = {"password": "newpass"}
        serializer = AdminUserSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        self.assertTrue(updated.check_password("newpass"))
        self.assertNotEqual(updated.password, "newpass")


class GroupSerializerTest(TestCase):
    def test_member_count_and_member_ids(self):
        u1 = User.objects.create_user(username="u1", password="pass")
        u2 = User.objects.create_user(username="u2", password="pass")
        gt = GroupType.objects.create(name="Home")
        cur = Currency.objects.get_or_create(code="USD", defaults={"name": "USD", "symbol": "$"})[0]
        group = Group.objects.create(
            name="G", group_type=gt, currency=cur, created_by=u1
        )
        group.members.add(u1, u2)
        serializer = GroupSerializer(group)
        self.assertEqual(serializer.data["member_count"], 2)
        self.assertCountEqual(serializer.data["member_ids"], [u1.pk, u2.pk])


class InputValidationTest(TestCase):
    """Tests for issue #8: input length & content validation."""

    def test_group_name_max_length(self):
        s = GroupSerializer(data={"name": "x" * 101, "default_split_method": "equal"})
        self.assertFalse(s.is_valid())
        self.assertIn("name", s.errors)

    def test_group_name_trims_whitespace(self):
        cur = Currency.objects.get_or_create(code="USD", defaults={"name": "USD", "symbol": "$"})[0]
        s = GroupSerializer(data={"name": "  Trip  ", "currency": cur.pk, "default_split_method": "equal"})
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data["name"], "Trip")

    def test_expense_description_max_length(self):
        s = ExpenseSerializer(data={
            "amount": "10.00", "description": "x" * 501, "date": "2026-01-01",
        })
        self.assertFalse(s.is_valid())
        self.assertIn("description", s.errors)

    def test_expense_description_rejects_control_chars(self):
        s = ExpenseSerializer(data={
            "amount": "10.00", "description": "hello\x00world", "date": "2026-01-01",
        })
        self.assertFalse(s.is_valid())
        self.assertIn("description", s.errors)

    def test_expense_description_allows_newline_tab(self):
        s = ExpenseSerializer(data={
            "amount": "10.00", "description": "line1\nline2\ttab", "date": "2026-01-01",
        })
        self.assertTrue(s.is_valid(), s.errors)

    def test_expense_description_trims_whitespace(self):
        s = ExpenseSerializer(data={
            "amount": "10.00", "description": "  Dinner  ", "date": "2026-01-01",
        })
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data["description"], "Dinner")

    def test_expense_amount_max_digits(self):
        s = ExpenseSerializer(data={
            "amount": "12345678901.00", "description": "Big", "date": "2026-01-01",
        })
        self.assertFalse(s.is_valid())
        self.assertIn("amount", s.errors)

    def test_user_display_name_max_length(self):
        s = UserSerializer(data={"display_name": "x" * 101})
        self.assertFalse(s.is_valid())
        self.assertIn("display_name", s.errors)

    def test_user_display_name_trims_whitespace(self):
        s = UserSerializer(data={"display_name": "  Alice  "})
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data["display_name"], "Alice")

    def test_category_name_max_length(self):
        s = CategorySerializer(data={"name": "x" * 51})
        self.assertFalse(s.is_valid())
        self.assertIn("name", s.errors)

    def test_currency_code_max_length(self):
        s = CurrencySerializer(data={"code": "ABCD", "name": "Test", "symbol": "$"})
        self.assertFalse(s.is_valid())
        self.assertIn("code", s.errors)

    def test_currency_name_max_length(self):
        s = CurrencySerializer(data={"code": "TST", "name": "x" * 51, "symbol": "$"})
        self.assertFalse(s.is_valid())
        self.assertIn("name", s.errors)

    def test_group_type_name_max_length(self):
        s = GroupTypeSerializer(data={"name": "x" * 51})
        self.assertFalse(s.is_valid())
        self.assertIn("name", s.errors)

    def test_settlement_amount_max_digits(self):
        s = SettlementSerializer(data={
            "amount": "12345678901.00", "payee": 1, "date": "2026-01-01",
        })
        self.assertFalse(s.is_valid())
        self.assertIn("amount", s.errors)
