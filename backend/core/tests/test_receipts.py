from io import BytesIO

from django.test import TestCase
from PIL import Image
from rest_framework.test import APIClient

from core.models import Expense, Group, ReceiptImage, User


def _make_image(size_bytes=100):
    """Create a small valid image file."""
    img = Image.new('RGB', (10, 10), color='red')
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    buf.name = 'receipt.png'
    return buf


class ReceiptUploadTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.creator = User.objects.create_user(username='creator', password='pass')
        self.other = User.objects.create_user(username='other', password='pass')
        self.group = Group.objects.create(name='G', created_by=self.creator)
        self.group.members.add(self.creator, self.other)
        self.client.force_login(self.creator)
        resp = self.client.post(f'/api/groups/{self.group.pk}/expenses/', {
            'amount': '50.00', 'description': 'Test', 'date': '2026-01-01',
        }, format='json')
        self.expense_id = resp.json()['id']

    def test_upload_receipt_success(self):
        self.client.force_login(self.creator)
        resp = self.client.post(
            f'/api/expenses/{self.expense_id}/receipts/',
            {'image': _make_image()},
            format='multipart',
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertIn('id', data)
        self.assertIn('image', data)
        self.assertEqual(ReceiptImage.objects.filter(expense_id=self.expense_id).count(), 1)

    def test_upload_no_image_returns_400(self):
        self.client.force_login(self.creator)
        resp = self.client.post(
            f'/api/expenses/{self.expense_id}/receipts/',
            {},
            format='multipart',
        )
        self.assertEqual(resp.status_code, 400)

    def test_upload_by_non_creator_returns_403(self):
        self.client.force_login(self.other)
        resp = self.client.post(
            f'/api/expenses/{self.expense_id}/receipts/',
            {'image': _make_image()},
            format='multipart',
        )
        self.assertEqual(resp.status_code, 403)

    def test_upload_max_5_receipts(self):
        self.client.force_login(self.creator)
        for _ in range(5):
            ReceiptImage.objects.create(expense_id=self.expense_id, image='receipts/test.png')
        resp = self.client.post(
            f'/api/expenses/{self.expense_id}/receipts/',
            {'image': _make_image()},
            format='multipart',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn('Maximum 5', resp.json()['detail'])

    def test_upload_too_large_returns_400(self):
        self.client.force_login(self.creator)
        # Create a file that exceeds 5MB
        large_file = BytesIO(b'x' * (5 * 1024 * 1024 + 1))
        large_file.name = 'big.png'
        resp = self.client.post(
            f'/api/expenses/{self.expense_id}/receipts/',
            {'image': large_file},
            format='multipart',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn('too large', resp.json()['detail'])

    def test_upload_to_nonexistent_expense_returns_404(self):
        self.client.force_login(self.creator)
        resp = self.client.post(
            '/api/expenses/99999/receipts/',
            {'image': _make_image()},
            format='multipart',
        )
        self.assertEqual(resp.status_code, 404)
