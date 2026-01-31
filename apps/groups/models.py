from django.db import models
from apps.common.models import Basemodel

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

    name = models.CharField(max_length=255, verbose_name="Guruh nomi")
    start_time = models.CharField(max_length=20)
    end_time = models.CharField(max_length=20)
    class_days = models.JSONField(default=list, blank=True, null=True, verbose_name="Dars kunlari (Du, Chor, Ju | Se, Pa, Sha)")
    
    # Teacher (o'qituvchi) - Foreign Key
    teacher = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='teaching_groups',
        limit_choices_to={'role': 'teacher'},
        verbose_name="O'qituvchi",
        null=True,
        blank=True
    )
    
    # Add students relation (many-to-many to User, limited to students)
    students = models.ManyToManyField(
        'users.User',
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