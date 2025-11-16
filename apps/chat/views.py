from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from .models import Message
from .serializers import MessageSerializer, MessageCreateSerializer


class MessageListView(generics.ListAPIView):
    """
    Xabarlarni olish
    
    GET /message/?admin_id={admin_uuid} - Student tomonidan (admindan xabarlar)
    GET /message/?student_id={student_uuid} - Admin tomonidan (studentdan xabarlar)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        """
        Xabarlarni filtrlash
        """
        user = self.request.user
        admin_id = self.request.query_params.get('admin_id')
        student_id = self.request.query_params.get('student_id')
        
        # Agar admin_id berilgan bo'lsa - student tomonidan admindan xabarlar
        if admin_id:
            return Message.objects.filter(
                Q(admin_id=admin_id, student=user) |
                Q(admin_id=admin_id, sender=user)
            ).order_by('-created_at')
        
        # Agar student_id berilgan bo'lsa - admin tomonidan studentdan xabarlar
        if student_id:
            return Message.objects.filter(
                Q(student_id=student_id, admin=user) |
                Q(student_id=student_id, sender=user)
            ).order_by('-created_at')
        
        # Agar hech qaysi filter berilmagan bo'lsa - bo'sh ro'yxat
        return Message.objects.none()


class MessageCreateView(generics.CreateAPIView):
    """
    Xabar yuborish
    
    POST /message/
    
    Student tomonidan adminiga xabar:
    {
        "text": "Xabar matni",
        "admin_id": "admin-uuid",
        "file": [File object] (optional)
    }
    
    Admin tomonidan studentga xabar:
    {
        "text": "Xabar matni",
        "student_id": "student-uuid",
        "file": [File object] (optional)
    }
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MessageCreateSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def create(self, request, *args, **kwargs):
        """
        Xabar yaratish
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Response uchun MessageSerializer ishlatish
        message = serializer.instance
        response_serializer = MessageSerializer(message, context={'request': request})
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
