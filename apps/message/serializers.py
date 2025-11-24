from rest_framework import serializers
from django.utils import timezone
from .models import MessagesModel


class MessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessagesModel
        fields = ['id', 'user_id', 'user_name', 'phone_number', 
                 'message', 'send_time', 'status', 'created_at']
        read_only_fields = ['owner', 'created_at']

    def validate_phone_number(self, value):
        if not value.startswith('+998'):
            raise serializers.ValidationError("Telefon raqam +998 bilan boshlanishi kerak")
        if len(value) != 13:
            raise serializers.ValidationError("Telefon raqam 13 ta belgidan iborat bo'lishi kerak")
        return value
        