import os
import mimetypes
import base64
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from drf_extra_fields.fields import Base64ImageField
from rest_framework_simplejwt.tokens import RefreshToken


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
    image_qrkod = serializers.SerializerMethodField()

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

    def get_image_qrkod(self, obj):
        """
        Return base64 data URI for QR image:
        - Prefer file in MEDIA_ROOT/qrcodesall whose filename starts with obj.uuid (e.g. ITC100.png)
        - Fallback to obj.image_qrkod (ImageField) if present
        - Return None if no image available
        """
        # prefer uuid-based file lookup
        uuid_val = getattr(obj, "uuid", None)
        qr_dir = os.path.join(settings.MEDIA_ROOT, "qrcodesall")

        def _encode_file(path):
            try:
                with open(path, "rb") as f:
                    data = f.read()
                mime, _ = mimetypes.guess_type(path)
                if not mime:
                    mime = "application/octet-stream"
                b64 = base64.b64encode(data).decode("utf-8")
                return f"data:{mime};base64,{b64}"
            except Exception:
                return None

        if uuid_val:
            try:
                for fname in os.listdir(qr_dir):
                    if fname.startswith(str(uuid_val)):
                        full = os.path.join(qr_dir, fname)
                        if os.path.isfile(full):
                            return _encode_file(full)
            except FileNotFoundError:
                pass  # qrcodesall folder not present

        # fallback: use image_qrkod ImageField on the model if set
        image_field = getattr(obj, "image_qrkod", None)
        if image_field:
            try:
                path = image_field.path
                if os.path.isfile(path):
                    return _encode_file(path)
            except Exception:
                # image_field may be a URL-only field or missing file
                try:
                    # try to resolve by MEDIA_ROOT + name
                    name = getattr(image_field, "name", None)
                    if name:
                        path = os.path.join(settings.MEDIA_ROOT, name)
                        if os.path.isfile(path):
                            return _encode_file(path)
                except Exception:
                    pass

        return None


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
            "tg_username",
            "direction",
            "phone_number",
            "password",
        ]

    def validate(self, attrs):
        username = attrs.get("username")
        phone_number = attrs.get("phone_number")
        uuid = attrs.get("uuid")

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "❌ Bu username allaqachon ro'yxatdan o'tgan."})

        if User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError({"phone_number": "❌ Bu telefon raqam allaqachon ro'yxatdan o'tgan."})

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
