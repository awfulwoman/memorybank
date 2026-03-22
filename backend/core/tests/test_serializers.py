from decimal import Decimal

from django.test import TestCase, RequestFactory

from core.models import Category, Currency, Group, GroupType, User
from core.serializers import AdminUserSerializer, ExpenseSerializer, GroupSerializer


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
        cur = Currency.objects.create(name="USD", symbol="$", code="USD")
        group = Group.objects.create(
            name="G", group_type=gt, currency=cur, created_by=u1
        )
        group.members.add(u1, u2)
        serializer = GroupSerializer(group)
        self.assertEqual(serializer.data["member_count"], 2)
        self.assertCountEqual(serializer.data["member_ids"], [u1.pk, u2.pk])
