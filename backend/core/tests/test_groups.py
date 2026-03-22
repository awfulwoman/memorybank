from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Currency, Group, GroupType, User


class GroupCRUDTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(username="admin", password="pass", is_staff=True)
        self.regular = User.objects.create_user(username="alice", password="pass", is_staff=False)
        self.cur = Currency.objects.get_or_create(code="USD", defaults={"name": "USD", "symbol": "$"})[0]
        self.gt = GroupType.objects.create(name="Home")

    def test_staff_create_group(self):
        self.client.force_login(self.staff)
        resp = self.client.post("/api/groups/", {
            "name": "New Group",
            "currency": self.cur.pk,
            "group_type": self.gt.pk,
        })
        self.assertEqual(resp.status_code, 201)

    def test_non_staff_create_group(self):
        self.client.force_login(self.regular)
        resp = self.client.post("/api/groups/", {
            "name": "My Group",
            "currency": self.cur.pk,
        })
        self.assertEqual(resp.status_code, 201)
        group = Group.objects.get(name="My Group")
        self.assertEqual(group.created_by, self.regular)
        self.assertIn(self.regular, group.members.all())

    def test_staff_create_group_also_added_to_members(self):
        self.client.force_login(self.staff)
        resp = self.client.post("/api/groups/", {
            "name": "Staff Group",
            "currency": self.cur.pk,
        })
        self.assertEqual(resp.status_code, 201)
        group = Group.objects.get(name="Staff Group")
        self.assertIn(self.staff, group.members.all())

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


class GroupOwnershipPermissionTest(TestCase):
    """Integration tests for US-004: ownership permission on update/delete."""

    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(username="admin", password="pass", is_staff=True)
        self.owner = User.objects.create_user(username="owner", password="pass", is_staff=False)
        self.other = User.objects.create_user(username="other", password="pass", is_staff=False)
        self.cur = Currency.objects.get_or_create(code="USD", defaults={"name": "USD", "symbol": "$"})[0]
        self.group = Group.objects.create(name="OwnedGroup", created_by=self.owner)
        self.group.members.add(self.owner, self.other)

    def test_non_owner_non_staff_patch_returns_403(self):
        self.client.force_login(self.other)
        resp = self.client.patch(f"/api/groups/{self.group.pk}/", {"name": "Hacked"}, content_type="application/json")
        self.assertEqual(resp.status_code, 403)

    def test_owner_patch_returns_200(self):
        self.client.force_login(self.owner)
        resp = self.client.patch(f"/api/groups/{self.group.pk}/", {"name": "Renamed"}, content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.group.refresh_from_db()
        self.assertEqual(self.group.name, "Renamed")

    def test_staff_patch_returns_200(self):
        self.client.force_login(self.staff)
        resp = self.client.patch(f"/api/groups/{self.group.pk}/", {"name": "StaffEdit"}, content_type="application/json")
        self.assertEqual(resp.status_code, 200)

    def test_owner_delete_returns_204(self):
        self.client.force_login(self.owner)
        resp = self.client.delete(f"/api/groups/{self.group.pk}/")
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Group.objects.filter(pk=self.group.pk).exists())

    def test_non_owner_non_staff_delete_returns_403(self):
        self.client.force_login(self.other)
        resp = self.client.delete(f"/api/groups/{self.group.pk}/")
        self.assertEqual(resp.status_code, 403)


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


class GroupMemberOwnerPermissionTest(TestCase):
    """Integration tests for US-005: group owner can manage members."""

    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(username="admin", password="pass", is_staff=True)
        self.owner = User.objects.create_user(username="owner", password="pass", is_staff=False)
        self.other = User.objects.create_user(username="other", password="pass", is_staff=False)
        self.target = User.objects.create_user(username="target", password="pass", is_staff=False)
        self.group = Group.objects.create(name="OwnedGroup", created_by=self.owner)
        self.group.members.add(self.owner, self.other)

    def test_owner_add_member(self):
        self.client.force_login(self.owner)
        resp = self.client.post(f"/api/groups/{self.group.pk}/members/", {"user_id": self.target.pk})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.target, self.group.members.all())

    def test_owner_remove_member(self):
        self.group.members.add(self.target)
        self.client.force_login(self.owner)
        resp = self.client.delete(f"/api/groups/{self.group.pk}/members/{self.target.pk}/")
        self.assertEqual(resp.status_code, 204)
        self.assertNotIn(self.target, self.group.members.all())

    def test_non_owner_non_staff_add_member_returns_403(self):
        self.client.force_login(self.other)
        resp = self.client.post(f"/api/groups/{self.group.pk}/members/", {"user_id": self.target.pk})
        self.assertEqual(resp.status_code, 403)

    def test_non_owner_non_staff_remove_member_returns_403(self):
        self.group.members.add(self.target)
        self.client.force_login(self.other)
        resp = self.client.delete(f"/api/groups/{self.group.pk}/members/{self.target.pk}/")
        self.assertEqual(resp.status_code, 403)

    def test_staff_can_add_member_to_any_group(self):
        self.client.force_login(self.staff)
        resp = self.client.post(f"/api/groups/{self.group.pk}/members/", {"user_id": self.target.pk})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.target, self.group.members.all())
