from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Currency, Group, GroupType, User


class GroupCRUDTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(username="admin", password="pass", is_staff=True)
        self.regular = User.objects.create_user(username="alice", password="pass", is_staff=False)
        self.cur = Currency.objects.create(name="USD", symbol="$", code="USD")
        self.gt = GroupType.objects.create(name="Home")

    def test_staff_create_group(self):
        self.client.force_login(self.staff)
        resp = self.client.post("/api/groups/", {
            "name": "New Group",
            "currency": self.cur.pk,
            "group_type": self.gt.pk,
        })
        self.assertEqual(resp.status_code, 201)

    def test_non_staff_sees_only_own_groups(self):
        g1 = Group.objects.create(name="G1", created_by=self.staff)
        g1.members.add(self.regular)
        g2 = Group.objects.create(name="G2", created_by=self.staff)
        # regular is NOT a member of g2

        self.client.force_login(self.regular)
        resp = self.client.get("/api/groups/")
        names = [g["name"] for g in resp.json()]
        self.assertIn("G1", names)
        self.assertNotIn("G2", names)

    def test_staff_sees_all_groups(self):
        before = Group.objects.count()
        Group.objects.create(name="G1", created_by=self.staff)
        Group.objects.create(name="G2", created_by=self.staff)
        self.client.force_login(self.staff)
        resp = self.client.get("/api/groups/")
        self.assertEqual(len(resp.json()), before + 2)


class GroupMemberTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(username="admin", password="pass", is_staff=True)
        self.alice = User.objects.create_user(username="alice", password="pass")
        self.bob = User.objects.create_user(username="bob", password="pass")
        self.group = Group.objects.create(name="G", created_by=self.staff)
        self.group.members.add(self.staff)
        self.client.force_login(self.staff)

    def test_add_member(self):
        resp = self.client.post(f"/api/groups/{self.group.pk}/members/", {"user_id": self.alice.pk})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.alice, self.group.members.all())

    def test_add_nonexistent_user_returns_404(self):
        resp = self.client.post(f"/api/groups/{self.group.pk}/members/", {"user_id": 9999})
        self.assertEqual(resp.status_code, 404)

    def test_remove_member(self):
        self.group.members.add(self.alice)
        resp = self.client.delete(f"/api/groups/{self.group.pk}/members/{self.alice.pk}/")
        self.assertEqual(resp.status_code, 204)
        self.assertNotIn(self.alice, self.group.members.all())
