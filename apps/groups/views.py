from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from apps.users.permissions import IsAdmin
from .models import Group
from .serializers import GroupSerializer

# Create your views here.

class GroupsViewSet(viewsets.ModelViewSet):
    """
    CRUD for Group model.
    - Read (list/retrieve): any authenticated user
    - Create/Update/Delete: only users with IsAdmin permission
    """
    queryset = Group.objects.all().order_by('-created_at')
    serializer_class = GroupSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'smena']
    search_fields = ['name', 'smena']
    ordering_fields = ['created_at', 'name', 'start_time']

    def get_permissions(self):
        """
        Allow authenticated read access, require IsAdmin for unsafe methods.
        """
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]
