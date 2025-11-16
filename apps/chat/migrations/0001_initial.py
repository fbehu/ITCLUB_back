# Generated migration for Message model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('text', models.TextField(verbose_name='Xabar matni')),
                ('file', models.FileField(blank=True, null=True, upload_to='messages/', verbose_name='Fayl')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqti')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")),
                ('admin', models.ForeignKey(blank=True, limit_choices_to={'role': 'admin'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='admin_messages', to=settings.AUTH_USER_MODEL, verbose_name='Admin')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL, verbose_name='Yuboruvchi')),
                ('student', models.ForeignKey(blank=True, limit_choices_to={'role': 'student'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_messages', to=settings.AUTH_USER_MODEL, verbose_name='Student')),
            ],
            options={
                'verbose_name': 'Xabar',
                'verbose_name_plural': 'Xabarlar',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['admin', 'created_at'], name='messages_me_admin_i_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['student', 'created_at'], name='messages_me_student_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['sender', 'created_at'], name='messages_me_sender_idx'),
        ),
    ]
