from django.db import models
from apps.groups.models import Group

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Kelgan'),
        ('absent', 'Kelmagan'),
        ('excuse', 'Sababli'),
    ]
    
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='attendances', verbose_name="Group")
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='attendances', verbose_name="User", null=True, blank=True)
    date = models.DateField(verbose_name="Date")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True, blank=True, verbose_name="Attendance Status")
    reason = models.CharField(max_length=255, null=True, blank=True, verbose_name="Reason (Sababli bo'lsa)")
    coins = models.IntegerField(default=0, verbose_name="Ball (o'sha kun uchun)", blank=True, null=True)

    class Meta:
        unique_together = ('group', 'user', 'date')
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"

    def __str__(self):
        return f"{self.group.name} - {self.user.username if self.user else 'No User'} - {self.date} - {self.status}"