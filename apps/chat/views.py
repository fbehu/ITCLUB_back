from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q, Count
from .models import Message
from .serializers import MessageSerializer, MessageCreateSerializer, UnreadCountSerializer, ConversationUserSerializer, UnreadNotificationSerializer


class UnreadMessageCountView(generics.ListAPIView):
    """
    O'qilmagan xabarlarni olish (notifications)
    
    GET /api/message/unread-count/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UnreadNotificationSerializer
    pagination_class = None
    
    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(admin=user, is_read=False) | Q(student=user, is_read=False)
        ).exclude(sender=user).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """
        O'qilmagan xabarlar list qaytarish
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

class ReadMessageView(generics.GenericAPIView):
    """
    Xabarlarni o'qilgan deb belgilash
    
    POST /api/message/mark-read/
    {
        "user_id": "user-uuid"
    }
    """
    permission_classes = [IsAuthenticated]
    serializer_class = None  # Serializer kerak emas
    
    def post(self, request, *args, **kwargs):
        user = request.user
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {"detail": "user_id kerak."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Shu userdan kelgan va o'qilmagan xabarlarni o'qilgan deb belgilash
        messages = Message.objects.filter(
            Q(sender_id=user_id, admin=user, is_read=False) |
            Q(sender_id=user_id, student=user, is_read=False)
        )
        
        updated_count = messages.update(is_read=True)
        
        return Response(
            {"detail": f"{updated_count} ta xabar o'qilgan deb belgilandi."},
            status=status.HTTP_200_OK
        )

class ConversationListView(generics.ListAPIView):
    """
    Userlarni conversations bilan birga ko'rsatish
    
    GET /api/message/conversations/?page=1 - Barcha conversations user list bilan
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationUserSerializer
    pagination_class = None
    
    def get_queryset(self):
        """
        Foydalanuvchiga bog'liq unique userlarni olish
        """
        from django.db.models import Q, F
        from apps.users.models import User
        
        current_user = self.request.user
        
        # Xabar almashgan userlarni olish
        user_ids = Message.objects.filter(
            Q(admin=current_user) | Q(student=current_user) | Q(sender=current_user)
        ).values_list('admin_id', 'student_id', 'sender_id').distinct()
        
        # Barcha user IDlarni yig'ish
        all_user_ids = set()
        for admin_id, student_id, sender_id in user_ids:
            if admin_id and admin_id != current_user.id:
                all_user_ids.add(admin_id)
            if student_id and student_id != current_user.id:
                all_user_ids.add(student_id)
            if sender_id and sender_id != current_user.id:
                all_user_ids.add(sender_id)
        
        return User.objects.filter(id__in=all_user_ids).order_by('-id')
    
    def list(self, request, *args, **kwargs):
        """
        Paginated user list qaytarish
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class MessageListView(generics.ListAPIView):
    """
    Xabarlarni olish (Conversations messages)
    
    GET /api/message/messages/?page=1&admin_id={admin_uuid} - Student tomonidan (admindan xabarlar)
    GET /api/message/messages/?page=1&student_id={student_uuid} - Admin tomonidan (studentdan xabarlar)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    pagination_class = None
    
    def get_queryset(self):
        """
        Xabarlarni filtrlash
        """
        user = self.request.user
        admin_id = self.request.query_params.get('admin_id')
        student_id = self.request.query_params.get('student_id')
        
        if admin_id:
            return Message.objects.filter(
                Q(admin_id=admin_id, student=user) |
                Q(admin_id=admin_id, sender=user)
            ).order_by('-created_at')
        
        if student_id:
            return Message.objects.filter(
                Q(student_id=student_id, admin=user) |
                Q(student_id=student_id, sender=user)
            ).order_by('-created_at')
        
        return Message.objects.none()
    
    def list(self, request, *args, **kwargs):
        """
        Paginated response qaytarish
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


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
