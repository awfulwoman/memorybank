from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    display_name = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    class Meta:
        db_table = 'core_user'


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

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
