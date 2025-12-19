from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import os

User = get_user_model()


class Message(models.Model):
    """
    Xabar modeli - admin va student o'rtasidagi xabarlarni saqlash uchun
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Xabar matni
    text = models.CharField(max_length=300, verbose_name="Xabar matni")
    
    # Admin va student - faqat bittasi null bo'lishi kerak
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='admin_messages',
        limit_choices_to={'role': 'admin'},
        verbose_name="Admin"
    )
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='student_messages',
        limit_choices_to={'role': 'student'},
        verbose_name="Student"
    )
    
    # Yuboruvchi (admin yoki student)
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name="Yuboruvchi"
    )
    
    # Fayl (ixtiyoriy)
    file = models.FileField(
        upload_to='messages/',
        null=True,
        blank=True,
        verbose_name="Fayl"
    )
    
    # O'qilganlik holati
    is_read = models.BooleanField(default=False, verbose_name="O'qilganmi?")
    
    # Vaqtlar
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")
    
    class Meta:
        verbose_name = "Xabar"
        verbose_name_plural = "Xabarlar"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['admin', 'created_at']),
            models.Index(fields=['student', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
        ]
    
    def __str__(self):
        if self.admin:
            return f"Admin {self.admin.username} -> Student {self.student.username}"
        else:
            return f"Student {self.student.username} -> Admin {self.admin.username}"
    
    @property
    def file_name(self):
        """Fayl nomini qaytaradi"""
        if self.file:
            return os.path.basename(self.file.name)
        return None
    
    @property
    def file_url(self):
        """Fayl URLini qaytaradi"""
        if self.file:
            return self.file.url
        return None
