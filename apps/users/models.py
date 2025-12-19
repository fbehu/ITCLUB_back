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

    COURSES = (
        ('kurs-1', '1-kurs'),
        ('kurs-2', '2-kurs'),
        ('kurs-3', '3-kurs'),
        ('kurs-4', '4-kurs'),
        ('kurs-5', '5-kurs'),
    )
    # Primary key as a UUID. Ensure the DB stores UUID strings (36 chars) before switching.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uuid = models.CharField(max_length=7, unique=True, null=True, blank=True, verbose_name="QR UUID")
    image_qrkod = models.ImageField(upload_to='qr_codes/', null=True, blank=True, verbose_name="QR code image")
    phone_number = models.CharField(max_length=20, blank=True, unique=True, verbose_name="Phone number")
    tg_username = models.CharField(max_length=150, blank=True, verbose_name="Telegram username")
    level = models.CharField(choices=LEVELS, max_length=50, blank=True, verbose_name="Level")
    course = models.CharField(choices=COURSES, max_length=50, blank=True, verbose_name="Course")
    direction = models.CharField(max_length=255, blank=True, verbose_name="Direction")
    coins = models.IntegerField(default=0, verbose_name="Coins")
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