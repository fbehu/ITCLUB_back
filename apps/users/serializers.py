from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from drf_extra_fields.fields import Base64ImageField
from rest_framework_simplejwt.tokens import RefreshToken
import base64


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
#  BASE64 ga o‘girish fieldi
# ============================
class ImageToBase64Field(serializers.ImageField):
    def to_internal_value(self, data):
        # Agar fayl yuborilgan bo‘lsa
        if hasattr(data, "read"):
            file_content = data.read()
            encoded_string = base64.b64encode(file_content).decode("utf-8")
            return encoded_string

        # Agar base64 string yuborilgan bo‘lsa
        return data


# ============================
#  USER SERIALIZER
# ============================
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "uuid",
            "image_qrkod",
            "phone_number",
            "tg_username",
            "level",
            "course",
            "direction",
            "coins",
            "photo",
            "role",
            "is_active",
            "created_at",
            "updated_at",
        ]


# ============================
#  REGISTER SERIALIZER
# ============================
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "uuid",
            "level",
            "course",
            "direction",
            "phone_number",
            "password",
        ]

    def validate(self, attrs):
        username = attrs.get("username")
        phone_number = attrs.get("phone_number")
        uuid = attrs.get("uuid")

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "❌ Bu username allaqachon ro‘yxatdan o‘tgan."})

        if User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError({"phone_number": "❌ Bu telefon raqam allaqachon ro‘yxatdan o‘tgan."})

        if User.objects.filter(uuid=uuid).exists():
            raise serializers.ValidationError({"uuid": "❌ Bu QR kod allaqachon boshqa user uchun ishlatilgan."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get("username"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            uuid=validated_data.get("uuid"),
            level=validated_data.get("level"),
            course=validated_data.get("course"),
            direction=validated_data.get("direction"),
            phone_number=validated_data.get("phone_number"),
            password=validated_data.get("password"),
        )
        return user


# ============================
#  LOGIN SERIALIZER
# ============================
class LoginSerializer(serializers.Serializer):
    username_or_phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username_or_phone = data.get("username_or_phone")
        password = data.get("password")

        user = authenticate(phone_number=username_or_phone, password=password)

        if not user:
            user = authenticate(username=username_or_phone, password=password)

        if not user:
            raise serializers.ValidationError("Login yoki parol noto'g'ri")

        data["user"] = user
        return data


# ============================
#  PASSWORD CHANGE SERIALIZER
# ============================
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("confirm_password"):
            raise serializers.ValidationError({"new_password": "Yangi parollar mos emas."})
        return attrs
