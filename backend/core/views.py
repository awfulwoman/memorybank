import csv
import json
from collections import defaultdict
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from rest_framework import mixins, status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ApiKey, Category, Currency, Expense, Group, GroupType, ReceiptImage, Settlement, User
from .permissions import IsGroupMemberOrAdmin, IsGroupOwnerOrAdmin
from .serializers import (
    AdminUserSerializer, CategorySerializer, CurrencySerializer, ExpenseSerializer, GroupSerializer,
    GroupTypeSerializer, SettlementSerializer, UserSerializer,
)


class AdminWritePermission(IsAuthenticated):
    """Allow read to all authenticated users, write only to admins."""

    WRITE_METHODS = ('POST', 'PUT', 'PATCH', 'DELETE')

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.method in self.WRITE_METHODS:
            return request.user.is_staff
        return True


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [AdminWritePermission]


class GroupTypeViewSet(viewsets.ModelViewSet):
    queryset = GroupType.objects.all().order_by('name')
    serializer_class = GroupTypeSerializer
    permission_classes = [AdminWritePermission]


class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all().order_by('code')
    serializer_class = CurrencySerializer
    permission_classes = [AdminWritePermission]


class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]

MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB


@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        login(request, user)
        return Response({'detail': 'Logged in.', 'username': user.username, 'is_staff': user.is_staff})


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'detail': 'Logged out.'})


class MeView(APIView):
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MeAvatarView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        image = request.FILES.get('avatar')
        if not image:
            return Response({'detail': 'No image provided.'}, status=status.HTTP_400_BAD_REQUEST)
        if image.size > MAX_AVATAR_SIZE:
            return Response({'detail': 'Image too large. Max 5MB.'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.avatar = image
        request.user.save()
        return Response(UserSerializer(request.user).data)


class MeApiKeyView(APIView):
    def post(self, request):
        ApiKey.objects.filter(user=request.user).delete()
        key_value = ApiKey.generate_key()
        ApiKey.objects.create(user=request.user, key=key_value)
        return Response({'key': key_value}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        deleted, _ = ApiKey.objects.filter(user=request.user).delete()
        if not deleted:
            return Response({'detail': 'No API key found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsGroupOwnerOrAdmin()]
        return [AdminWritePermission()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Group.objects.all().order_by('name')
        return self.request.user.expense_groups.all().order_by('name')

    def perform_create(self, serializer):
        group = serializer.save(created_by=self.request.user)
        group.members.add(self.request.user)


class GroupMemberView(APIView):
    permission_classes = [IsGroupOwnerOrAdmin]

    def post(self, request, pk):
        group = Group.objects.get(pk=pk)
        user_id = request.data.get('user_id')
        username = request.data.get('username')
        try:
            if user_id:
                user = User.objects.get(pk=user_id)
            elif username:
                user = User.objects.get(username=username)
            else:
                return Response({'detail': 'user_id or username required.'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        group.members.add(user)
        return Response({'detail': f'{user.username} added to group.'}, status=status.HTTP_200_OK)

    def delete(self, request, pk, user_id):
        group = Group.objects.get(pk=pk)
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        group.members.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupExpenseView(APIView):
    permission_classes = [IsGroupMemberOrAdmin]

    def get(self, request, pk):
        group = Group.objects.get(pk=pk)
        expenses = Expense.objects.filter(group=group).select_related(
            'category', 'created_by'
        ).prefetch_related('splits__user').order_by('-date', '-created_at')
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        group = Group.objects.get(pk=pk)
        serializer = ExpenseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user, group=group)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ExpenseDetailView(APIView):
    def _get_expense(self, pk, user):
        try:
            expense = Expense.all_objects.get(pk=pk)
        except Expense.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound('Expense not found.')
        return expense

    def patch(self, request, pk):
        expense = self._get_expense(pk, request.user)
        if expense.created_by != request.user:
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ExpenseSerializer(expense, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        expense = self._get_expense(pk, request.user)
        if expense.created_by != request.user:
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        expense.is_deleted = True
        expense.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


MAX_RECEIPT_SIZE = 5 * 1024 * 1024  # 5MB
MAX_RECEIPTS_PER_EXPENSE = 5


class ExpenseReceiptView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, pk):
        try:
            expense = Expense.objects.get(pk=pk)
        except Expense.DoesNotExist:
            return Response({'detail': 'Expense not found.'}, status=status.HTTP_404_NOT_FOUND)
        if expense.created_by != request.user:
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        image = request.FILES.get('image')
        if not image:
            return Response({'detail': 'No image provided.'}, status=status.HTTP_400_BAD_REQUEST)
        if image.size > MAX_RECEIPT_SIZE:
            return Response({'detail': 'Image too large. Max 5MB.'}, status=status.HTTP_400_BAD_REQUEST)
        if expense.receipts.count() >= MAX_RECEIPTS_PER_EXPENSE:
            return Response({'detail': 'Maximum 5 receipts per expense.'}, status=status.HTTP_400_BAD_REQUEST)
        receipt = ReceiptImage.objects.create(expense=expense, image=image)
        return Response({'id': receipt.id, 'image': receipt.image.url}, status=status.HTTP_201_CREATED)


class GroupSettlementView(APIView):
    permission_classes = [IsGroupMemberOrAdmin]

    def get(self, request, pk):
        group = Group.objects.get(pk=pk)
        settlements = Settlement.objects.filter(group=group).select_related(
            'payer', 'payee'
        ).order_by('-date', '-created_at')
        serializer = SettlementSerializer(settlements, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        group = Group.objects.get(pk=pk)
        serializer = SettlementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payee_id = serializer.validated_data.get('payee').id if serializer.validated_data.get('payee') else request.data.get('payee')
        if not group.members.filter(pk=payee_id).exists():
            return Response(
                {'payee': ['Payee must be a member of the group.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save(payer=request.user, group=group)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


def _compute_balances(expenses, settlements):
    """
    Returns (net_balances, pairwise_debts).
    net_balances: dict {user_id: Decimal}  (positive = owed money, negative = owes money)
    pairwise_debts: list of {from_user_id, from_username, to_user_id, to_username, amount}
    """
    # amount owed[debtor][creditor] = amount
    owes = defaultdict(lambda: defaultdict(Decimal))

    for expense in expenses:
        payer = expense.created_by
        if payer is None:
            continue
        for split in expense.splits.all():
            if split.user != payer:
                owes[split.user_id][payer.id] += split.amount

    for settlement in settlements:
        # payer paid payee => reduces payer's debt to payee
        owes[settlement.payer_id][settlement.payee_id] -= settlement.amount

    # Simplify: net out A->B and B->A
    pairs = set()
    for a in list(owes.keys()):
        for b in list(owes[a].keys()):
            if (b, a) not in pairs:
                pairs.add((a, b))

    pairwise = []
    for a, b in pairs:
        net = owes[a][b] - owes[b][a]
        if net > 0:
            pairwise.append({'from_user_id': a, 'to_user_id': b, 'amount': net})
        elif net < 0:
            pairwise.append({'from_user_id': b, 'to_user_id': a, 'amount': -net})

    # Net per user (positive = others owe them)
    net_balances = defaultdict(Decimal)
    for item in pairwise:
        net_balances[item['from_user_id']] -= item['amount']
        net_balances[item['to_user_id']] += item['amount']

    return net_balances, pairwise


class GroupBalanceView(APIView):
    permission_classes = [IsGroupMemberOrAdmin]

    def get(self, request, pk):
        group = Group.objects.get(pk=pk)
        expenses = (
            Expense.objects.filter(group=group)
            .select_related('created_by')
            .prefetch_related('splits__user')
        )
        settlements = Settlement.objects.filter(group=group).select_related('payer', 'payee')

        net_balances, pairwise = _compute_balances(expenses, settlements)

        # Enrich pairwise with usernames
        user_ids = set()
        for item in pairwise:
            user_ids.add(item['from_user_id'])
            user_ids.add(item['to_user_id'])
        users = {u.id: u for u in User.objects.filter(id__in=user_ids)}

        for item in pairwise:
            from_user = users.get(item['from_user_id'])
            to_user = users.get(item['to_user_id'])
            item['from_username'] = from_user.username if from_user else ''
            item['from_display_name'] = (from_user.display_name or from_user.username) if from_user else ''
            item['to_username'] = to_user.username if to_user else ''
            item['to_display_name'] = (to_user.display_name or to_user.username) if to_user else ''
            item['amount'] = str(item['amount'])

        member_balances = [
            {'user_id': uid, 'username': users.get(uid, None) and users[uid].username, 'display_name': (users[uid].display_name or users[uid].username) if uid in users else '', 'balance': str(bal)}
            for uid, bal in net_balances.items()
        ]

        return Response({'balances': member_balances, 'debts': pairwise})


class MeBalanceView(APIView):
    def get(self, request):
        user = request.user
        groups = user.expense_groups.all()
        total_net = defaultdict(Decimal)
        group_details = []

        for group in groups:
            expenses = (
                Expense.objects.filter(group=group)
                .select_related('created_by')
                .prefetch_related('splits__user')
            )
            settlements = Settlement.objects.filter(group=group).select_related('payer', 'payee')
            net_balances, pairwise = _compute_balances(expenses, settlements)

            user_balance = net_balances.get(user.id, Decimal('0'))
            total_net[user.id] += user_balance

            # filter pairwise to only involving this user
            user_debts = [
                item for item in pairwise
                if item['from_user_id'] == user.id or item['to_user_id'] == user.id
            ]
            group_details.append({
                'group_id': group.id,
                'group_name': group.name,
                'currency_symbol': group.currency.symbol if group.currency else '',
                'balance': str(user_balance),
                'debts': [{**d, 'amount': str(d['amount'])} for d in user_debts],
            })

        return Response({
            'total_balance': str(total_net.get(user.id, Decimal('0'))),
            'groups': group_details,
        })


def _expense_rows(expenses):
    rows = []
    for e in expenses:
        for split in e.splits.all():
            rows.append({
                'date': str(e.date),
                'amount': str(e.amount),
                'description': e.description,
                'category': e.category.name if e.category else '',
                'paid_by': (e.created_by.display_name or e.created_by.username) if e.created_by else '',
                'split_member': split.user.display_name or split.user.username,
                'split_amount': str(split.amount),
            })
        if not e.splits.exists():
            rows.append({
                'date': str(e.date),
                'amount': str(e.amount),
                'description': e.description,
                'category': e.category.name if e.category else '',
                'paid_by': (e.created_by.display_name or e.created_by.username) if e.created_by else '',
                'split_member': '',
                'split_amount': '',
            })
    return rows


def _render_export(rows, fmt, filename):
    if fmt == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        if rows:
            writer = csv.DictWriter(response, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        return response
    else:
        response = HttpResponse(
            json.dumps(rows, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}.json"'
        return response


class GroupExportView(APIView):
    permission_classes = [IsGroupMemberOrAdmin]

    def get(self, request, pk):
        fmt = request.query_params.get('format', 'csv')
        if fmt not in ('csv', 'json'):
            return Response({'detail': 'format must be csv or json'}, status=status.HTTP_400_BAD_REQUEST)
        group = Group.objects.get(pk=pk)
        expenses = (
            Expense.objects.filter(group=group)
            .select_related('category', 'created_by')
            .prefetch_related('splits__user')
            .order_by('date')
        )
        rows = _expense_rows(expenses)
        return _render_export(rows, fmt, f'group_{pk}_expenses')


class MeExportView(APIView):
    def get(self, request):
        fmt = request.query_params.get('format', 'csv')
        if fmt not in ('csv', 'json'):
            return Response({'detail': 'format must be csv or json'}, status=status.HTTP_400_BAD_REQUEST)
        expenses = (
            Expense.objects.filter(created_by=request.user)
            .select_related('category', 'created_by', 'group')
            .prefetch_related('splits__user')
            .order_by('date')
        )
        rows = _expense_rows(expenses)
        return _render_export(rows, fmt, 'my_expenses')
