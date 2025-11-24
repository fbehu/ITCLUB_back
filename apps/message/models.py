from django.db import models
from django.utils import timezone
from apps.common.models import Basemodel
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class MessagesModel(Basemodel):
    STATUS_CHOICES = [
        ('waiting', 'Kutilmoqda'),
        ('sending', 'Yuborilmoqda'),
        ('sent', 'Yuborildi'),
    ]
    
    user_id = models.CharField(max_length=200, verbose_name='User idsi')
    user_name = models.CharField(max_length=50, verbose_name='Xabar qabul qiluvchi Ismi')
    phone_number = models.CharField(max_length=13, verbose_name='Telefon raqam')
    message = models.TextField(verbose_name='Xabar matni')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Yuboruvchi')
    send_time = models.DateTimeField(verbose_name='Yuborish vaqti')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='waiting',
        verbose_name='Xabar holati'
    )
    
    class Meta:
        verbose_name = 'Sms yuborish'
        verbose_name_plural = 'Smslar'
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        # Only update status from 'waiting' to 'sending' if send_time has arrived
        if self.status == 'waiting' and self.send_time <= timezone.now():
            self.status = 'sending'
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.user_name} - {self.message[:50]}"
