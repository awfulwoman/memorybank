from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ApiKey
from .serializers import UserSerializer

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
