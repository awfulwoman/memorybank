from rest_framework import serializers
from .models import Category, Currency, Group, GroupType, User


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


class GroupSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    group_type_name = serializers.CharField(source='group_type.name', read_only=True)
    currency_code = serializers.CharField(source='currency.code', read_only=True)

    class Meta:
        model = Group
        fields = [
            'id', 'name', 'group_type', 'group_type_name',
            'currency', 'currency_code', 'default_split_method',
            'created_by', 'member_count',
        ]
        read_only_fields = ['created_by']

    def get_member_count(self, obj):
        return obj.members.count()
