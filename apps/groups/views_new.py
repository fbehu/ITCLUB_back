from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.users.permissions import IsAdmin
from django.contrib.auth import get_user_model
from .models import Group
from .serializers import GroupSerializer

User = get_user_model()

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
    filterset_fields = ['name']
    search_fields = ['name']
    ordering_fields = ['created_at', 'name', 'start_time']

    def get_permissions(self):
        """
        Allow authenticated read access, require IsAdmin for unsafe methods.
        """
        # Students action uchun alohida permission tekshiruvi
        if self.action == 'students':
            if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
                return [IsAuthenticated()]
            return [IsAuthenticated(), IsAdmin()]
        
        # Boshqa action-lar uchun
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]

    @action(detail=True, methods=['get', 'post'], url_path='students')
    def students(self, request, pk=None):
        """
        GET: Guruhga tgishli o'quvchilarning ma'lumotlarini ko'rsatadi
        POST: O'quvchilarni guruhga qo'shadi
        Expected POST body: {"student_ids": ["uuid1", "uuid2", ...]}
        """
        group = self.get_object()
        
        if request.method == 'GET':
            # GET - guruhga tgishli o'quvchilarni qaytaradi
            students = group.students.all()
            from apps.users.serializers import UserSerializer
            serializer = UserSerializer(students, many=True, context={'request': request})
            return Response({
                "count": students.count(),
                "students": serializer.data
            }, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            # POST - o'quvchilarni guruhga qo'shadi
            data = request.data or {}
            student_ids = data.get('student_ids')
            if not isinstance(student_ids, (list, tuple)):
                return Response({"detail": "student_ids list ko'rinishida bo'lishi kerak"}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch users that are students and whose id in provided list
            users_qs = User.objects.filter(id__in=student_ids, role='student')
            found_ids = set(str(u.id) for u in users_qs)
            requested_ids = set(str(s) for s in student_ids)
            missing_ids = list(requested_ids - found_ids)

            # Add found users to group (duplicates are ignored by add())
            if users_qs.exists():
                group.students.add(*users_qs)
            
            added_ids = list(found_ids)
            group_serializer = GroupSerializer(group, context={'request': request})
            return Response({
                "added_count": users_qs.count(),
                "added_ids": added_ids,
                "missing_ids": missing_ids,
                "group": group_serializer.data
            }, status=status.HTTP_201_CREATED)
