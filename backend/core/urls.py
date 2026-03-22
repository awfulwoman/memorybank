from django.urls import path
from .views import LoginView, LogoutView, MeApiKeyView, MeAvatarView, MeView

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('users/me/', MeView.as_view(), name='me'),
    path('users/me/avatar/', MeAvatarView.as_view(), name='me-avatar'),
    path('users/me/api-key/', MeApiKeyView.as_view(), name='me-api-key'),
]
