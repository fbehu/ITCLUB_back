from django.db import models
from apps.common.models import Basemodel

class Certificate(Basemodel):
    """
    Sertifikat modeli - foydalanuvchilarga berilgan sertifikatlarni saqlash uchun
    """
    name = models.CharField(max_length=255, verbose_name="Sertifikat nomi")
    description = models.TextField(blank=True, null=True, verbose_name="Sertifikat tavsifi")
    issued_date = models.DateField(verbose_name="Berilgan sana")
    photo = models.ImageField(upload_to='certificates/', blank=True, null=True, verbose_name="Sertifikat rasmi")
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='owned_certificates',
        verbose_name="Sertifikat egasi"
    )
    
    class Meta:
        verbose_name = "Sertifikat"
        verbose_name_plural = "Sertifikatlar"
        ordering = ['-issued_date']
        
    def __str__(self):
        return f"{self.name} - {self.owner.username}"