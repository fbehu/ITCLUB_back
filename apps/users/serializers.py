import os
import mimetypes
import base64
from django.conf import settings
from rest_framework import serializers
from .models import User
from drf_extra_fields.fields import Base64ImageField
from rest_framework_simplejwt.tokens import RefreshToken
from apps.groups.models import Group


def create_custom_jwt_for_user(user):
    refresh = RefreshToken.for_user(user)

    refresh["user_id"] = str(user.id)
    access = refresh.access_token
    access["user_id"] = str(user.id)

    return {
        "refresh": str(refresh),
        "access": str(access),
    }


# ============================
#  BASE64 ga o'girish fieldi
# ============================
class ImageToBase64Field(serializers.ImageField):
    def to_internal_value(self, data):
        # Agar fayl yuborilgan bo'lsa
        if hasattr(data, "read"):
            file_content = data.read()
            encoded_string = base64.b64encode(file_content).decode("utf-8")
            return encoded_string

        # Agar base64 string yuborilgan bo'lsa
        return data


# ============================
#  USER SERIALIZER
# ============================
class UserSerializer(serializers.ModelSerializer):
    student_groups = serializers.SerializerMethodField()
    teaching_groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "parent_phone_number",
            "tg_username",
            "level",
            "student_groups",
            "teaching_groups",
            "social",
            "invite_code",
            "coins",
            "photo",
            "role",
            "is_active",
            "created_at",
            "updated_at",
        ]

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


# ============================
#  STUDENT LIST SERIALIZER (guruhda o'quvchilarni ko'rsatish uchun)
# ============================
class StudentListSerializer(serializers.ModelSerializer):
    """Guruhga tegishli o'quvchilarning kerakli ma'lumotlarini qaytaradi"""
    
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "phone_number",
            "coins",
            "level",
            "photo",
        ]


# ============================
#  REGISTER SERIALIZER
# ============================
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), 
        many=True, 
        required=False,
        help_text="Student uchun: qo'shilish kerak bo'lgan guruhlar ID'lari. Teacher uchun: o'qitaydigan guruhlar ID'lari."
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "level",
            "groups",
            "tg_username",
            "social",
            "coins",
            "invite_code",
            "phone_number",
            "parent_phone_number",
            "role",
            "password",
        ]

    def validate(self, attrs):
        username = attrs.get("username")
        phone_number = attrs.get("phone_number")

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "❌ Bu username allaqachon ro'yxatdan o'tgan."})

        if User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError({"phone_number": "❌ Bu telefon raqam allaqachon ro'yxatdan o'tgan."})
        return attrs

    def create(self, validated_data):
        groups_data = validated_data.pop("groups", [])
        user = User.objects.create_user(
            username=validated_data.get("username"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            phone_number=validated_data.get("phone_number"),
            parent_phone_number=validated_data.get("parent_phone_number"),
            tg_username=validated_data.get("tg_username"),
            level=validated_data.get("level"),
            social=validated_data.get("social"),
            invite_code=validated_data.get("invite_code"),
            coins=validated_data.get("coins"),
            role=validated_data.get("role"),
            password=validated_data.get("password"),
        )
        
        # Agarda guruhlaar belgilangan bo'lsa, user'ni o'sha guruhlarga qo'shish
        if groups_data:
            if user.role == 'student':
                # Student uchun student_groups'ga qo'shish
                user.student_groups.set(groups_data)
            elif user.role == 'teacher':
                # Teacher uchun teaching_groups'ga qo'shish
                for group in groups_data:
                    group.teacher = user
                    group.save()
        
        return user


# ============================
#  ADMIN LIST SERIALIZER
# ============================
class AdminListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "photo",
        ]
