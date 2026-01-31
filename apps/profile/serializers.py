from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    student_groups = serializers.SerializerMethodField()
    teaching_groups = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'first_name', 
            'last_name', 
            'email', 
            'phone_number',
            'parent_phone_number', 
            'tg_username', 
            'level', 
            'student_groups',
            'teaching_groups',
            'social', 
            'coins', 
            'invite_code',
            'photo', 
            'role', 
            'created_at'
        ]
        read_only_fields = ['id', 'role', 'created_at', 'username']
    
    def get_student_groups(self, obj):
        """Student bo'lsa, qaysi guruhlarda o'qiyotganini qaytaradi"""
        if obj.role == 'student':
            groups = obj.student_groups.all()
            return [{"id": g.id, "name": g.name} for g in groups]
        return []
    
    def get_teaching_groups(self, obj):
        """Teacher bo'lsa, qaysi guruhlarda o'qitayotganini qaytaradi"""
        if obj.role == 'teacher':
            groups = obj.teaching_groups.all()
            return [{"id": g.id, "name": g.name} for g in groups]
        return []

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    new_password_confirm = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({'new_password': 'Parollar mos kelmadi'})
        validate_password(data['new_password'])
        return data
    
    def save(self, user):
        if not user.check_password(self.validated_data['old_password']):
            raise serializers.ValidationError({'old_password': 'Eski parol noto\'g\'ri'})
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class UserStatisticsSerializer(serializers.ModelSerializer):
    teaching_groups_count = serializers.SerializerMethodField()
    student_groups_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'role', 
            'teaching_groups_count', 'student_groups_count', 
            'level', 'coins', 'created_at'
        ]
    
    def get_teaching_groups_count(self, obj):
        return obj.teaching_groups.count()
    
    def get_student_groups_count(self, obj):
        return obj.student_groups.count()
