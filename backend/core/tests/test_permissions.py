from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Category, Currency, Group, GroupType, User


class AdminWritePermissionTest(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="admin", password="pass", is_staff=True)
        self.regular = User.objects.create_user(username="alice", password="pass", is_staff=False)
        self.client = APIClient()

    def test_non_staff_get_categories_200(self):
        self.client.force_login(self.regular)
        resp = self.client.get("/api/categories/")
        self.assertEqual(resp.status_code, 200)

    def test_non_staff_post_categories_403(self):
        self.client.force_login(self.regular)
        resp = self.client.post("/api/categories/", {"name": "Travel"})
        self.assertEqual(resp.status_code, 403)

    def test_staff_post_categories_201(self):
        self.client.force_login(self.staff)
        resp = self.client.post("/api/categories/", {"name": "Travel"})
        self.assertEqual(resp.status_code, 201)

    def test_staff_delete_categories_204(self):
        self.client.force_login(self.staff)
        cat = Category.objects.create(name="ToDelete")
        resp = self.client.delete(f"/api/categories/{cat.pk}/")
        self.assertEqual(resp.status_code, 204)

    def test_non_staff_post_groups_allowed(self):
        self.client.force_login(self.regular)
        cur = Currency.objects.create(name="USD", symbol="$", code="USD")
        gt = GroupType.objects.create(name="Home")
        resp = self.client.post("/api/groups/", {
            "name": "New Group",
            "currency": cur.pk,
            "group_type": gt.pk,
        })
        self.assertEqual(resp.status_code, 201)


class IsGroupOwnerOrAdminTest(TestCase):
    """Unit tests for IsGroupOwnerOrAdmin permission class."""

    def setUp(self):
        self.staff = User.objects.create_user(username="admin", password="pass", is_staff=True)
        self.owner = User.objects.create_user(username="owner", password="pass", is_staff=False)
        self.other = User.objects.create_user(username="other", password="pass", is_staff=False)
        self.group = Group.objects.create(name="TestGroup", created_by=self.owner)
        self.group.members.add(self.owner, self.other)

    def _check(self, user):
        from core.permissions import IsGroupOwnerOrAdmin
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user
        # Simulate view kwargs with group pk
        view = type("FakeView", (), {"kwargs": {"pk": self.group.pk}})()
        return IsGroupOwnerOrAdmin().has_permission(request, view)

    def test_owner_allowed(self):
        self.assertTrue(self._check(self.owner))

    def test_staff_allowed(self):
        self.assertTrue(self._check(self.staff))

    def test_non_owner_non_staff_denied(self):
        self.assertFalse(self._check(self.other))

    def test_nonexistent_group_denied(self):
        from core.permissions import IsGroupOwnerOrAdmin
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = self.owner
        view = type("FakeView", (), {"kwargs": {"pk": 99999}})()
        self.assertFalse(IsGroupOwnerOrAdmin().has_permission(request, view))

    def test_no_pk_in_kwargs_denied(self):
        from core.permissions import IsGroupOwnerOrAdmin
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = self.owner
        view = type("FakeView", (), {"kwargs": {}})()
        self.assertFalse(IsGroupOwnerOrAdmin().has_permission(request, view))
