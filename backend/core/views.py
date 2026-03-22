from django.contrib.auth import authenticate, login, logout
from rest_framework import mixins, status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ApiKey, Category, Currency, GroupType
from .serializers import CategorySerializer, CurrencySerializer, GroupTypeSerializer, UserSerializer


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
