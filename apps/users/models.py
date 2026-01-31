from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class User(AbstractUser):
    ROLES = (
        ('student', 'Student'),
        ('teacher', 'O\'qituvchi'),
        ('admin', 'Admin'),
    )

    LEVELS = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert'),
    )

    SOCIAL = (
        ('instagram', 'Instagram'),
        ('telegram', 'Telegram'),
        ('facebook', 'Facebook'),
        ('friend', 'Do\'st'),
        ('other', 'Boshqa'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, verbose_name="Phone number")
    parent_phone_number = models.JSONField(null=True, blank=True, verbose_name="Parent phone numbers")
    tg_username = models.CharField(max_length=150, blank=True, null=True, verbose_name="Telegram username")
    level = models.CharField(choices=LEVELS, max_length=50, blank=True, null=True, verbose_name="Level")
    social = models.CharField(choices=SOCIAL, max_length=255, blank=True, null=True, verbose_name="Social source")
    invite_code = models.CharField(max_length=50, blank=True,null=True, verbose_name="Invite code (PROMOKOD)")
    coins = models.IntegerField(default=0, verbose_name="Ball (0/100)", blank=True, null=True)
    photo = models.ImageField(upload_to="user_photos/", null=True, blank=True)

    role = models.CharField(choices=ROLES, max_length=50, default='student', verbose_name="Foydalanuvchi roli")
    is_active = models.BooleanField(default=True, verbose_name="Faol foydalanuvchi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=timezone.now) 

    USERNAME_FIELD = "phone_number" 
    REQUIRED_FIELDS = ["username"]  

    def __str__(self):
        return f"{self.username} ({self.phone_number})"
    
    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"