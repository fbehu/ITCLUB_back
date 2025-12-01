from rest_framework.permissions import BasePermission

class IsGroupMember(BasePermission):
    """
    Custom permission to only allow members of a group to access attendance records.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Check if the user is a member of the group associated with the attendance record
        return obj.group.members.filter(id=request.user.id).exists()