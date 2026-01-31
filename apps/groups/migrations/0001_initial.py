# Generated initial migration

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('name', models.CharField(max_length=255, verbose_name='Guruh nomi')),
                ('start_time', models.CharField(max_length=20)),
                ('end_time', models.CharField(max_length=20)),
                ('class_days', models.JSONField(blank=True, default=list, null=True, verbose_name='Dars kunlari (Du, Chor, Ju | Se, Pa, Sha)')),
                ('students', models.ManyToManyField(blank=True, related_name='student_groups', to=settings.AUTH_USER_MODEL, verbose_name='Students')),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='teaching_groups', to=settings.AUTH_USER_MODEL, verbose_name="O'qituvchi")),
            ],
            options={
                'verbose_name': 'Guruh',
                'verbose_name_plural': 'Guruhlar',
                'ordering': ['-created_at'],
            },
        ),
    ]
