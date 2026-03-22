from decimal import Decimal
from rest_framework import serializers
from .models import Category, Currency, Expense, ExpenseSplit, Group, GroupType, Settlement, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'avatar', 'is_staff']
        read_only_fields = ['id', 'username', 'avatar', 'is_staff']


class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'is_active', 'is_staff', 'password']
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon']


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
    member_ids = serializers.SerializerMethodField()
    members_list = serializers.SerializerMethodField()
    group_type_name = serializers.CharField(source='group_type.name', read_only=True)
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    currency_symbol = serializers.CharField(source='currency.symbol', read_only=True)
    currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all())

    class Meta:
        model = Group
        fields = [
            'id', 'name', 'icon', 'group_type', 'group_type_name',
            'currency', 'currency_code', 'currency_symbol', 'default_split_method',
            'created_by', 'member_count', 'member_ids', 'members_list',
        ]
        read_only_fields = ['created_by']

    def get_member_count(self, obj):
        return obj.members.count()

    def get_member_ids(self, obj):
        return list(obj.members.values_list('id', flat=True))

    def get_members_list(self, obj):
        return [
            {'id': m.id, 'username': m.username, 'display_name': m.display_name}
            for m in obj.members.all().order_by('username')
        ]


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
    created_by_display_name = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'amount', 'description', 'date', 'category', 'category_name', 'category_icon',
            'group', 'created_by', 'created_by_username', 'created_by_display_name', 'receipt_image',
            'is_deleted', 'created_at', 'updated_at', 'splits', 'split_data',
        ]
        read_only_fields = ['created_by', 'group', 'is_deleted', 'created_at', 'updated_at']

    def get_created_by_display_name(self, obj):
        if obj.created_by:
            return obj.created_by.display_name or obj.created_by.username
        return ''

    def validate_receipt_image(self, value):
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('Receipt image too large. Max 5MB.')
        return value

    def _create_splits(self, expense, split_data, members):
        expense.splits.all().delete()
        if split_data:
            member_ids = set(members.values_list('id', flat=True))
            split_user_ids = {s['user_id'] for s in split_data}
            non_members = split_user_ids - member_ids
            if non_members:
                raise serializers.ValidationError(
                    f'Users {non_members} are not members of this group.'
                )
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


class SettlementSerializer(serializers.ModelSerializer):
    payer_username = serializers.CharField(source='payer.username', read_only=True)
    payee_username = serializers.CharField(source='payee.username', read_only=True)
    payer_display_name = serializers.SerializerMethodField()
    payee_display_name = serializers.SerializerMethodField()

    class Meta:
        model = Settlement
        fields = ['id', 'group', 'payer', 'payer_username', 'payer_display_name', 'payee', 'payee_username', 'payee_display_name', 'amount', 'date', 'created_at']

    def get_payer_display_name(self, obj):
        return obj.payer.display_name or obj.payer.username if obj.payer else ''

    def get_payee_display_name(self, obj):
        return obj.payee.display_name or obj.payee.username if obj.payee else ''
        read_only_fields = ['payer', 'group', 'created_at']
