from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Group Name")

    def __str__(self):
        return self.name

class Attendance(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='attendances', verbose_name="Group")
    date = models.DateField(verbose_name="Date")
    status = models.BooleanField(default=False, verbose_name="Attendance Status")

    class Meta:
        unique_together = ('group', 'date')
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"

    def __str__(self):
        return f"{self.group.name} - {self.date} - {'Present' if self.status else 'Absent'}"