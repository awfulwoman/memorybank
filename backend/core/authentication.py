from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class ApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None

        from .models import ApiKey
        try:
            key_obj = ApiKey.objects.select_related('user').get(key=api_key)
        except ApiKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API key.')

        if not key_obj.user.is_active:
            raise AuthenticationFailed('User is inactive.')

        return (key_obj.user, key_obj)
