from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import News
from .serializers import NewsSerializer

class IsAdminRole(BasePermission):
    """Only users with admin role can write (POST, PUT, DELETE)"""
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        """Update news status (admin only)"""
        # Check if user is admin
        if request.user.role != 'admin':
            return Response(
                {'detail': 'Faqat admin rolida bo\'lgan userlar bu amalni bajara oladi.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            news = self.get_queryset().get(pk=pk)
        except News.DoesNotExist:
            return Response({'detail': 'No News matches the given query.'}, status=status.HTTP_404_NOT_FOUND)
        
        new_status = request.data.get('status')
        
        # Validate status
        valid_statuses = ['new', 'old']
        if new_status not in valid_statuses:
            return Response(
                {'detail': f'Status {valid_statuses} dan bittasi bo\'lishi kerak.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        news.status = new_status
        news.save()
        
        serializer = NewsSerializer(news)
        return Response(serializer.data, status=status.HTTP_200_OK)
