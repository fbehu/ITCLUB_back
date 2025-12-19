from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Faqat admin roliga ega foydalanuvchilarga ruxsat beradi.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin' or request.user.role == 'teacher')