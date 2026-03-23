from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    AdminUserViewSet,
    CategoryViewSet, CurrencyViewSet, GroupTypeViewSet, GroupViewSet,
    GroupBalanceView, GroupExpenseView, GroupExportView, GroupMemberView, GroupSettlementView,
    ExpenseDetailView, ExpenseReceiptView,
    LoginView, LogoutView, MeApiKeyView, MeAvatarView, MeBalanceView, MeExportView, MeView,
)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('group-types', GroupTypeViewSet, basename='grouptype')
router.register('currencies', CurrencyViewSet, basename='currency')
router.register('groups', GroupViewSet, basename='group')
router.register('admin/users', AdminUserViewSet, basename='admin-user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('users/me/', MeView.as_view(), name='me'),
    path('users/me/avatar/', MeAvatarView.as_view(), name='me-avatar'),
    path('users/me/api-key/', MeApiKeyView.as_view(), name='me-api-key'),
    path('users/me/balances/', MeBalanceView.as_view(), name='me-balances'),
    path('users/me/export/', MeExportView.as_view(), name='me-export'),
    path('groups/<int:pk>/members/', GroupMemberView.as_view(), name='group-members'),
    path('groups/<int:pk>/members/<int:user_id>/', GroupMemberView.as_view(), name='group-member-detail'),
    path('groups/<int:pk>/expenses/', GroupExpenseView.as_view(), name='group-expenses'),
    path('groups/<int:pk>/settlements/', GroupSettlementView.as_view(), name='group-settlements'),
    path('groups/<int:pk>/balances/', GroupBalanceView.as_view(), name='group-balances'),
    path('groups/<int:pk>/export/', GroupExportView.as_view(), name='group-export'),
    path('expenses/<int:pk>/', ExpenseDetailView.as_view(), name='expense-detail'),
    path('expenses/<int:pk>/receipts/', ExpenseReceiptView.as_view(), name='expense-receipts'),
    path('expenses/<int:pk>/receipts/<int:receipt_id>/', ExpenseReceiptView.as_view(), name='expense-receipt-detail'),
]
