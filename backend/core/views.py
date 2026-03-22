from django.contrib.auth import authenticate, login, logout
from rest_framework import mixins, status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ApiKey, Category, Currency, Expense, Group, GroupType, Settlement, User
from .serializers import (
    CategorySerializer, CurrencySerializer, ExpenseSerializer, GroupSerializer,
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

MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB


class LoginView(APIView):
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
    permission_classes = [AdminWritePermission]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Group.objects.all().order_by('name')
        return self.request.user.expense_groups.all().order_by('name')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class GroupMemberView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        group = Group.objects.get(pk=pk)
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(pk=user_id)
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


class GroupSettlementView(APIView):
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
        serializer.save(payer=request.user, group=group)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
