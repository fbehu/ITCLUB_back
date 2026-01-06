from django.db import models
from apps.common.models import Basemodel

class News(Basemodel):
    TYPE_CHOICES = [
        ('feature', 'Yangi funksiya'),
        ('improvement', 'Yaxshilash'),
        ('announcement', 'E\'lon'),
        ('bugfix', 'Xato tuzatish'),
    ]
    STATUS_CHOICES = [
        ('new', 'Yangi'),
        ('old', 'Eski'),
    ]
    title = models.CharField(max_length=150)
    description = models.TextField()
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='announcement', verbose_name='Yangilik turi')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Holati', blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']