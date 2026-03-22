from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, CurrencyViewSet, GroupTypeViewSet,
    LoginView, LogoutView, MeApiKeyView, MeAvatarView, MeView,
)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('group-types', GroupTypeViewSet, basename='grouptype')
router.register('currencies', CurrencyViewSet, basename='currency')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('users/me/', MeView.as_view(), name='me'),
    path('users/me/avatar/', MeAvatarView.as_view(), name='me-avatar'),
    path('users/me/api-key/', MeApiKeyView.as_view(), name='me-api-key'),
]
