import secrets

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    display_name = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    class Meta:
        db_table = 'core_user'


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default='mdi-shape-outline', blank=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class GroupType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Currency(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name_plural = 'currencies'

    def __str__(self):
        return f'{self.code} ({self.symbol})'


class Group(models.Model):
    SPLIT_EQUAL = 'equal'
    SPLIT_CUSTOM = 'custom'
    SPLIT_CHOICES = [
        (SPLIT_EQUAL, 'Equal'),
        (SPLIT_CUSTOM, 'Custom'),
    ]

    name = models.CharField(max_length=200)
    icon = models.CharField(max_length=50, default='mdi-account-group', blank=True)
    group_type = models.ForeignKey(GroupType, on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    default_split_method = models.CharField(max_length=10, choices=SPLIT_CHOICES, default=SPLIT_EQUAL)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_groups'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='expense_groups', blank=True
    )

    def __str__(self):
        return self.name


class ExpenseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Expense(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=500)
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='expenses'
    )
    receipt_image = models.ImageField(upload_to='receipts/', blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ExpenseManager()
    all_objects = models.Manager()

    def __str__(self):
        return f'{self.description} ({self.amount})'


class ExpenseSplit(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='splits')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expense_splits'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def clean(self):
        from django.core.exceptions import ValidationError
        total = self.expense.splits.exclude(pk=self.pk).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        if total + self.amount != self.expense.amount:
            raise ValidationError('Sum of splits must equal expense amount.')

    def __str__(self):
        return f'{self.user} owes {self.amount} for {self.expense}'


class Settlement(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='settlements')
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='settlements_paid'
    )
    payee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='settlements_received'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.payer} paid {self.payee} {self.amount}'


class ReceiptImage(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='receipts')
    image = models.ImageField(upload_to='receipts/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Receipt for {self.expense}'


class ApiKey(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='api_key'
    )
    key = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def generate_key(cls):
        return secrets.token_hex(32)

    def __str__(self):
        return f'ApiKey for {self.user}'
