from django.db import models
from django.contrib.auth import get_user_model
from apps.common.models import Basemodel

User = get_user_model()

class Group(Basemodel):
    """
    Guruh modeli - foydalanuvchilar guruhlarini saqlash uchun
    """
    class_days = [
        ('monday', 'Dushanba'),
        ('tuesday', 'Seshanba'),
        ('wednesday', 'Chorshanba'),
        ('thursday', 'Payshanba'),
        ('friday', 'Juma'),
        ('saturday', 'Shanba'),
        ('sunday', 'Yakshanba'),
    ]
    name = models.CharField(max_length=255, verbose_name="Guruh nomi")
    smena = models.CharField(max_length=500, verbose_name="Guruh Smenasi")
    start_time = models.CharField(max_length=500, verbose_name="Guruh Smenasi")
    
    class Meta:
        verbose_name = "Guruh"
        verbose_name_plural = "Guruhlar"
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name