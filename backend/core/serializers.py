from decimal import Decimal
from rest_framework import serializers
from .models import Category, Currency, Expense, ExpenseSplit, Group, GroupType, User


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


class ExpenseSplitSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ExpenseSplit
        fields = ['id', 'user', 'username', 'amount']


class ExpenseSerializer(serializers.ModelSerializer):
    splits = ExpenseSplitSerializer(many=True, read_only=True)
    split_data = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'amount', 'description', 'date', 'category', 'category_name',
            'group', 'created_by', 'created_by_username', 'receipt_image',
            'is_deleted', 'created_at', 'updated_at', 'splits', 'split_data',
        ]
        read_only_fields = ['created_by', 'group', 'is_deleted', 'created_at', 'updated_at']

    def validate_receipt_image(self, value):
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('Receipt image too large. Max 5MB.')
        return value

    def _create_splits(self, expense, split_data, members):
        expense.splits.all().delete()
        if split_data:
            total = sum(Decimal(str(s['amount'])) for s in split_data)
            if total != expense.amount:
                raise serializers.ValidationError('Sum of splits must equal expense amount.')
            for s in split_data:
                ExpenseSplit.objects.create(
                    expense=expense,
                    user_id=s['user_id'],
                    amount=Decimal(str(s['amount'])),
                )
        else:
            # Equal split
            member_list = list(members)
            n = len(member_list)
            if n > 0:
                share = (expense.amount / n).quantize(Decimal('0.01'))
                for member in member_list:
                    ExpenseSplit.objects.create(expense=expense, user=member, amount=share)

    def create(self, validated_data):
        split_data = validated_data.pop('split_data', None)
        expense = Expense.objects.create(**validated_data)
        self._create_splits(expense, split_data, expense.group.members.all())
        return expense

    def update(self, instance, validated_data):
        split_data = validated_data.pop('split_data', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if split_data is not None:
            self._create_splits(instance, split_data, instance.group.members.all())
        return instance
