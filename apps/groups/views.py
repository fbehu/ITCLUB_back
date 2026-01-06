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

class GroupsViewSet(viewsets.ModelViewSet):
    """
    CRUD for Group model with role-based permissions:
    - Admin: Create/Read/Update/Delete all groups, manage students
    - Teacher: Read only own groups (where teacher=current_user), Update own groups, Manage students
    - Student: Read only own groups (where student is in students)
    """
    serializer_class = GroupSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'smena']
    search_fields = ['name', 'smena']
    ordering_fields = ['created_at', 'name', 'start_time']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter groups based on user role"""
        user = self.request.user
        
        if user.role == 'admin':
            # Admin can see all groups
            return Group.objects.all().order_by('-created_at')
        elif user.role == 'teacher':
            # Teacher can see only their own groups
            return Group.objects.filter(teacher=user).order_by('-created_at')
        elif user.role == 'student':
            # Student can see only groups they're part of
            return Group.objects.filter(students=user).order_by('-created_at')
        
        return Group.objects.none()

    def get_permissions(self):
        """Role-based permissions"""
        if self.action in ['create', 'destroy']:
            # Only admin can create/delete groups
            return [IsAuthenticated(), IsAdmin()]
        elif self.action in ['update', 'partial_update']:
            # Admin can update any group, teacher can update their own
            return [IsAuthenticated()]
        elif self.action == 'students':
            # Admin and teacher can manage students
            return [IsAuthenticated()]
        
        # Default: authenticated users can list/retrieve
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        """Only admin or teacher can update groups"""
        group = self.get_object()
        user = request.user
        
        if user.role == 'admin':
            return super().update(request, *args, **kwargs)
        elif user.role == 'teacher' and group.teacher == user:
            return super().update(request, *args, **kwargs)
        else:
            return Response(
                {"detail": "Siz bu guruhni o'zgartira olmaysiz."},
                status=status.HTTP_403_FORBIDDEN
            )

    def destroy(self, request, *args, **kwargs):
        """Only admin can delete groups"""
        user = request.user
        
        if user.role != 'admin':
            return Response(
                {"detail": "Faqat admin guruhni o'chira oladi."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get', 'post', 'delete'], url_path='students')
    def students(self, request, pk=None):
        """
        GET: Guruhga tgishli o'quvchilarning ma'lumotlarini ko'rsatadi
        POST: Admin va teacher o'quvchilarni guruhga qo'shadi
        DELETE: Admin va teacher o'quvchini guruhdan o'chiradi
        """
        group = self.get_object()
        user = request.user
        
        if request.method == 'GET':
            # Barcha rol'dagi userlar o'quvchilarni ko'rishi mumkin
            students = group.students.all()
            from apps.users.serializers import UserSerializer
            serializer = UserSerializer(students, many=True, context={'request': request})
            return Response({
                "count": students.count(),
                "students": serializer.data
            }, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            # Faqat admin va teacher o'quvchilarni qo'shishi mumkin
            if user.role not in ['admin', 'teacher']:
                return Response(
                    {"detail": "Siz o'quvchilarni guruhga qo'sha olmaysiz."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Teacher o'zining guruhlari uchun qo'sha oladi
            if user.role == 'teacher' and group.teacher != user:
                return Response(
                    {"detail": "Siz bu guruhga o'quvchilarni qo'sha olmaysiz."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            data = request.data or {}
            student_ids = data.get('student_ids')
            if not isinstance(student_ids, (list, tuple)):
                return Response(
                    {"detail": "student_ids list ko'rinishida bo'lishi kerak"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Faqat student rolida o'lgan userlarni qo'shish
            users_qs = User.objects.filter(id__in=student_ids, role='student')
            found_ids = set(str(u.id) for u in users_qs)
            requested_ids = set(str(s) for s in student_ids)
            missing_ids = list(requested_ids - found_ids)

            # Allaqachon guruhdagi o'quvchilarni topish
            already_in_group = []
            for student in users_qs:
                if group.students.filter(id=student.id).exists():
                    already_in_group.append(str(student.id))

            if already_in_group:
                return Response({
                    "detail": "Bu o'quvchilar allaqachon ushbu guruhda mavjud",
                    "already_in_group": already_in_group,
                    "message": "O'quvchilarni qo'shib bo'lmadi"
                }, status=status.HTTP_400_BAD_REQUEST)

            if users_qs.exists():
                group.students.add(*users_qs)
            
            group_serializer = GroupSerializer(group, context={'request': request})
            return Response({
                "added_count": users_qs.count(),
                "added_ids": list(found_ids),
                "missing_ids": missing_ids,
                "group": group_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        elif request.method == 'DELETE':
            # Faqat admin va teacher o'quvchini guruhdan o'chirishi mumkin
            if user.role not in ['admin', 'teacher']:
                return Response(
                    {"detail": "Siz o'quvchini guruhdan o'chira olmaysiz."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Teacher o'zining guruhlari uchun o'chirishi mumkin
            if user.role == 'teacher' and group.teacher != user:
                return Response(
                    {"detail": "Siz bu guruhdan o'quvchini o'chira olmaysiz."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            data = request.data or {}
            student_id = data.get('student_id')
            
            if not student_id:
                return Response(
                    {"detail": "student_id kerak"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                student = User.objects.get(id=student_id, role='student')
                # Faqat guruhdan olib tashlash, o'quvchini o'chirisdan emas
                group.students.remove(student)
                group_serializer = GroupSerializer(group, context={'request': request})
                return Response({
                    "message": "O'quvchi guruhdan olib tashlandi",
                    "student_id": str(student.id),
                    "student_name": f"{student.first_name} {student.last_name}",
                    "group": group_serializer.data
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response(
                    {"detail": "O'quvchi topilmadi"},
                    status=status.HTTP_404_NOT_FOUND
                )

    @action(detail=True, methods=['post'], url_path='transfer-student')
    def transfer_student(self, request, pk=None):
        """
        O'quvchini bir guruhdan boshqa guruhga o'tkazish
        
        POST /api/groups/{group_id}/transfer-student/
        Body:
        {
            "student_id": "student-uuid",
            "target_group_id": "target-group-id"
        }
        """
        source_group = self.get_object()
        user = request.user
        
        # Faqat admin va teacher o'quvchini o'tkazishi mumkin
        if user.role not in ['admin', 'teacher']:
            return Response(
                {"detail": "Siz o'quvchini o'tkaza olmaysiz."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Teacher o'zining guruhlari uchun o'tkazishi mumkin
        if user.role == 'teacher' and source_group.teacher != user:
            return Response(
                {"detail": "Siz bu guruhdan o'quvchini o'tkaza olmaysiz."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data or {}
        student_id = data.get('student_id')
        target_group_id = data.get('target_group_id')
        
        if not student_id or not target_group_id:
            return Response(
                {"detail": "student_id va target_group_id kerak"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            student = User.objects.get(id=student_id, role='student')
        except User.DoesNotExist:
            return Response(
                {"detail": "O'quvchi topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            target_group = Group.objects.get(id=target_group_id)
        except Group.DoesNotExist:
            return Response(
                {"detail": "Maqsadli guruh topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # O'quvchi manba guruhda borligini tekshirish
        if not source_group.students.filter(id=student.id).exists():
            return Response(
                {"detail": "O'quvchi ushbu guruhda mavjud emas"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # O'quvchi maqsadli guruhda borligini tekshirish
        if target_group.students.filter(id=student.id).exists():
            return Response(
                {"detail": "O'quvchi allaqachon maqsadli guruhda mavjud"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # O'quvchini manba guruhdan olib tashlash va maqsadli guruhga qo'shish
        source_group.students.remove(student)
        target_group.students.add(student)
        
        return Response({
            "message": f"O'quvchi muvaffaqiyatli o'tkazildi",
            "student_id": str(student.id),
            "student_name": f"{student.first_name} {student.last_name}",
            "from_group": {
                "id": source_group.id,
                "name": source_group.name
            },
            "to_group": {
                "id": target_group.id,
                "name": target_group.name
            }
        }, status=status.HTTP_200_OK)
