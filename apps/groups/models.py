from django.db import models
from django.contrib.auth import get_user_model
from apps.common.models import Basemodel

User = get_user_model()

class Group(Basemodel):
    """
    Guruh modeli - foydalanuvchilar guruhlarini saqlash uchun
    """
    CLASSDAYS = [
        ('monday', 'Dushanba'),
        ('tuesday', 'Seshanba'),
        ('wednesday', 'Chorshanba'),
        ('thursday', 'Payshanba'),
        ('friday', 'Juma'),
        ('saturday', 'Shanba'),
        ('sunday', 'Yakshanba'),
    ]
    class_days = models.CharField(choices=CLASSDAYS, max_length=50, verbose_name="Dars kunlari")
    name = models.CharField(max_length=255, verbose_name="Guruh nomi")
    smena = models.CharField(max_length=500, verbose_name="Guruh Smenasi", blank=True)
    start_time = models.CharField(max_length=20, blank=True, null=True)
    
    # Add students relation (many-to-many to User, limited to students)
    students = models.ManyToManyField(
        User,
        blank=True,
        related_name='student_groups',
        limit_choices_to={'role': 'student'},
        verbose_name="Students"
    )
    
    class Meta:
        verbose_name = "Guruh"
        verbose_name_plural = "Guruhlar"
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name