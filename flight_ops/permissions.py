from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Grant permission to read data to anyone
    and limit creating and editing data to admin users only.
    """
    def has_permission(self, request, view):
        return bool(
            (request.method in SAFE_METHODS)
            or (request.user and request.user.is_staff)
        )
