from django.test import TestCase

from core.models import (
    ApiKey,
    Category,
    Currency,
    Expense,
    Group,
    GroupType,
    User,
)


class UserModelTest(TestCase):
    def test_create_user_with_display_name(self):
        user = User.objects.create_user(
            username="testuser", password="pass123", display_name="Test User"
        )
        self.assertEqual(user.display_name, "Test User")
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.check_password("pass123"))


class CategoryModelTest(TestCase):
    def test_str(self):
        cat = Category.objects.create(name="Food")
        self.assertEqual(str(cat), "Food")


class GroupTypeModelTest(TestCase):
    def test_str(self):
        gt = GroupType.objects.create(name="Home")
        self.assertEqual(str(gt), "Home")


class CurrencyModelTest(TestCase):
    def test_str(self):
        cur = Currency.objects.create(name="US Dollar", symbol="$", code="USD")
        self.assertEqual(str(cur), "USD ($)")


class GroupModelTest(TestCase):
    def test_create_with_members_and_default_split(self):
        user1 = User.objects.create_user(username="u1", password="pass")
        user2 = User.objects.create_user(username="u2", password="pass")
        group = Group.objects.create(name="Test Group", default_split_method="equal")
        group.members.add(user1, user2)
        self.assertEqual(group.members.count(), 2)
        self.assertEqual(group.default_split_method, "equal")
        self.assertEqual(str(group), "Test Group")


class ExpenseManagerTest(TestCase):
    def test_soft_delete_excluded_from_default_manager(self):
        user = User.objects.create_user(username="u1", password="pass")
        group = Group.objects.create(name="G")
        exp = Expense.all_objects.create(
            amount=100,
            description="Test",
            date="2026-01-01",
            group=group,
            created_by=user,
            is_deleted=False,
        )
        deleted_exp = Expense.all_objects.create(
            amount=50,
            description="Deleted",
            date="2026-01-01",
            group=group,
            created_by=user,
            is_deleted=True,
        )
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(Expense.all_objects.count(), 2)
        self.assertIn(exp, Expense.objects.all())
        self.assertNotIn(deleted_exp, Expense.objects.all())
        self.assertIn(deleted_exp, Expense.all_objects.all())


class ApiKeyModelTest(TestCase):
    def test_generate_key_returns_64_char_hex(self):
        key = ApiKey.generate_key()
        self.assertEqual(len(key), 64)
        # Verify it's valid hex
        int(key, 16)
