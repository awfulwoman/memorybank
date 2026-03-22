from rest_framework import serializers
from .models import Category, Currency, GroupType, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'avatar', 'is_staff']
        read_only_fields = ['id', 'username', 'avatar', 'is_staff']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class GroupTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupType
        fields = ['id', 'name']


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'name', 'symbol', 'code']
