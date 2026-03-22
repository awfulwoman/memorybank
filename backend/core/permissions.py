from rest_framework.permissions import IsAuthenticated

from .models import Group


class IsGroupMemberOrAdmin(IsAuthenticated):
    """Allow access only to group members or staff users."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        group_pk = view.kwargs.get('pk')
        if group_pk is None:
            return False
        try:
            group = Group.objects.get(pk=group_pk)
        except Group.DoesNotExist:
            return False
        if request.user.is_staff:
            return True
        return group.members.filter(pk=request.user.pk).exists()
