from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Certificate
from .serializers import CertificateSerializer, CertificateListSerializer
from django.shortcuts import get_object_or_404


class CertificateViewSet(viewsets.ModelViewSet):
    """
    Sertifikat APIsi
    
    Admin: Barcha sertifikatlarni CRUD qiladi
    Boshqa userlar: Faqat o'z sertifikatlarini ko'radi
    """
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Foydalanuvchiga tegishli sertifikatlarni filtrlaymiz"""
        user = self.request.user
        
        # Admin barcha sertifikatlarni ko'radi
        if user.role == 'admin':
            return Certificate.objects.all().order_by('-issued_date')
        
        # Boshqa userlar faqat o'zlariga tegishli sertifikatlarni ko'radi
        return Certificate.objects.filter(owner=user).order_by('-issued_date')
    
    def get_serializer_class(self):
        """Create va update uchun CertificateSerializer, list/retrieve uchun CertificateListSerializer"""
        if self.action in ['list', 'retrieve']:
            return CertificateListSerializer
        return CertificateSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Sertifikat qo'shish - faqat admin qila oladi
        POST /api/certificates/
        
        {
            "name": "Python Expert",
            "description": "Python Sertifikati",
            "issued_date": "2026-01-31",
            "owner_id": "o'quvchi_uuid",
            "photo": <file>
        }
        """
        # Faqat admin sertifikat qo'sha oladi
        if request.user.role != 'admin':
            return Response(
                {"detail": "Sertifikat qo'shish uchun siz boshliq bo'lishingiz kerak brooo  :("},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """
        Sertifikat o'zgartirish - faqat admin qila oladi
        PUT /api/certificates/{id}/
        """
        # Faqat admin o'zgartirsih qila oladi
        if request.user.role != 'admin':
            return Response(
                {"detail": "Sertifikat o'zgartirish uchun siz boshliq bo'lishingiz kerak brooo :)."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Sertifikat qisman o'zgartirish - faqat admin qila oladi
        PATCH /api/certificates/{id}/
        """
        # Faqat admin o'zgartirsih qila oladi
        if request.user.role != 'admin':
            return Response(
                {"detail": "Sertifikat o'zgartirish uchun siz boshliq bo'lishingiz kerak brooo :)."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Sertifikat o'chirish - faqat admin qila oladi
        DELETE /api/certificates/{id}/
        """
        # Faqat admin o'chirish qila oladi
        if request.user.role != 'admin':
            return Response(
                {"detail": "Sertifikat o'chirish uchun admin roliga ega bo'lish kerak."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)
