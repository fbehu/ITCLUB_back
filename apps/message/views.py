from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MessagesModel
from .serializers import MessagesSerializer
from .permissions import IsValidAndroidDevices
from uuid import UUID
from apps.users.permissions import IsAdmin

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessagesSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user_id', 'status'] 
    search_fields = ['user_name', 'phone_number', 'message']
    ordering_fields = ['send_time', 'created_at']
    
    def get_queryset(self):
        queryset = MessagesModel.objects.filter(owner=self.request.user)
        
        # Filter by user_id if provided
        user_id = self.request.query_params.get('user_id')
        if user_id:
            try:
                user_id = UUID(user_id)  # Validate UUID format
                queryset = queryset.filter(user_id=user_id)
            except ValueError:
                return queryset.none()  # Return empty queryset if invalid UUID
        
        # Update status for messages where send_time has passed
        current_time = timezone.now()
        waiting_messages = queryset.filter(status='waiting', send_time__lte=current_time)
        if waiting_messages.exists():
            waiting_messages.update(status='sending')
            
        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        # This will trigger the status update
        self.get_queryset()
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        # This will trigger the status update
        self.get_queryset()
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        send_time = serializer.validated_data['send_time']
        initial_status = 'sending' if send_time <= timezone.now() else 'waiting'
        serializer.save(
            owner=self.request.user,
            status=initial_status
        )


class MessagesListView(APIView):
    authentication_classes = []  
    permission_classes = [IsValidAndroidDevices]  

    def get(self, request, *args, **kwargs):
        current_time = timezone.now()
        queryset = MessagesModel.objects.all()

        # Update waiting messages if their time has come
        waiting_messages = queryset.filter(status='waiting', send_time__lte=current_time)
        if waiting_messages.exists():
            waiting_messages.update(status='sending')

        # Filter by status if provided in query params
        status = request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        serializer = MessagesSerializer(queryset.order_by('-created_at'), many=True)
        return Response(serializer.data)

    def patch(self, request, pk=None, *args, **kwargs):
        if not pk:
            return Response({"error": "Message ID kerak"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            instance = MessagesModel.objects.get(pk=pk)
        except MessagesModel.DoesNotExist:
            return Response({"error": "Message topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        # Only allow updating to 'sent' status if current status is 'sending'
        if request.data.get('status') == 'sent' and instance.status != 'sending':
            return Response(
                {"error": "Faqat yuborilayotgan xabarni yakunlangan holatga o'tkazish mumkin"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Don't allow changing status back to 'waiting' or 'sending' if already 'sent'
        if instance.status == 'sent':
            return Response(
                {"error": "Yuborilgan xabarning holatini o'zgartirib bo'lmaydi"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = MessagesSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)