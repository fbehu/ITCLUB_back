from rest_framework import serializers
from .models import Certificate
from apps.users.models import User
from apps.users.serializers import UserSerializer


class CertificateSerializer(serializers.ModelSerializer):
    """Sertifikat serializer - qo'shish va o'zgartirish uchun"""
    owner_id = serializers.CharField(write_only=True, required=True)  # Qo'shish uchun
    owner = UserSerializer(read_only=True)  # Response uchun
    
    class Meta:
        model = Certificate
        fields = ['id', 'name', 'description', 'issued_date', 'photo', 'owner_id', 'owner', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
    
    def validate_owner_id(self, value):
        """Owner foydalanuvchi mavjudligini tekshirish"""
        try:
            user = User.objects.get(id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Bu ID'ga ega foydalanuvchi topilmadi.")
    
    def create(self, validated_data):
        """Sertifikat yaratishda owner'ni qo'yish"""
        owner_id = validated_data.pop('owner_id')
        validated_data['owner_id'] = owner_id
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Sertifikat o'zgartirishda owner'ni yangilash"""
        owner_id = validated_data.pop('owner_id', None)
        if owner_id:
            validated_data['owner_id'] = owner_id
        return super().update(instance, validated_data)


class CertificateListSerializer(serializers.ModelSerializer):
    """Sertifikat listini ko'rsatish uchun"""
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    owner_id = serializers.CharField(source='owner.id', read_only=True)
    
    class Meta:
        model = Certificate
        fields = ['id', 'name', 'description', 'issued_date', 'photo', 'owner_id', 'owner_username', 'created_at']
        read_only_fields = ['id', 'created_at']
