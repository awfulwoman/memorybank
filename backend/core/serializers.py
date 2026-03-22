from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'avatar', 'is_staff']
        read_only_fields = ['id', 'username', 'avatar', 'is_staff']
