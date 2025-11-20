from rest_framework import serializers
from .models import Message
from apps.users.models import User
from django.db.models import Q, Count
import os
from django.conf import settings
import mimetypes
import base64

class MessageSerializer(serializers.ModelSerializer):
    """
    Xabarlarni olish uchun serializer
    """
    sender_name = serializers.SerializerMethodField()
    admin_id = serializers.SerializerMethodField()
    student_id = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id',
            'text',
            'admin_id',
            'student_id',
            'sender_name',
            'created_at',
            'file_url',
            'file_name',
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_sender_name(self, obj):
        """Yuboruvchi ismini qaytaradi"""
        return f"{obj.sender.first_name} {obj.sender.last_name}".strip()
    
    def get_admin_id(self, obj):
        """Admin IDni qaytaradi (agar admin yuborgan bo'lsa)"""
        if obj.admin:
            return str(obj.admin.id)
        return None
    
    def get_student_id(self, obj):
        """Student IDni qaytaradi (agar student yuborgan bo'lsa)"""
        if obj.student:
            return str(obj.student.id)
        return None
    
    def get_file_url(self, obj):
        """Fayl URLini qaytaradi"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def get_file_name(self, obj):
        """Fayl nomini qaytaradi"""
        return obj.file_name


class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Xabar yuborish uchun serializer
    """
    admin_id = serializers.CharField(required=False, allow_blank=True)
    student_id = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField(required=False, allow_null=True)
    
    class Meta:
        model = Message
        fields = [
            'id',
            'text',
            'admin_id',
            'student_id',
            'file',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate(self, data):
        """
        Validatsiya:
        - admin_id va student_id dan faqat bittasi bo'lishi kerak
        - Fayl hajmi 50MB dan oshmasligi kerak
        - Fayl formati ruxsat etilgan bo'lishi kerak
        """
        admin_id = data.get('admin_id')
        student_id = data.get('student_id')
        file = data.get('file')
        
        # admin_id va student_id dan faqat bittasi bo'lishi kerak
        if not admin_id and not student_id:
            raise serializers.ValidationError(
                "admin_id yoki student_id ni jo'natish majburiy"
            )
        
        if admin_id and student_id:
            raise serializers.ValidationError(
                "Faqat admin_id yoki student_id ni jo'natish mumkin, ikkalasini emas"
            )
        
        # Fayl validatsiyasi
        if file:
            # Maksimal hajm: 50MB
            max_size = 50 * 1024 * 1024  # 50MB
            if file.size > max_size:
                raise serializers.ValidationError(
                    {"file": "Fayl hajmi 50MB dan oshmasligi kerak"}
                )
            
            # Ruxsat etilgan formatlar
            allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.docx', '.xlsx']
            file_ext = '.' + file.name.split('.')[-1].lower()
            
            if file_ext not in allowed_extensions:
                raise serializers.ValidationError(
                    {"file": f"Ruxsat etilgan formatlar: {', '.join(allowed_extensions)}"}
                )
        
        return data
    
    def create(self, validated_data):
        """
        Xabar yaratish
        """
        request = self.context.get('request')
        sender = request.user
        
        admin_id = validated_data.pop('admin_id', None)
        student_id = validated_data.pop('student_id', None)
        
        # Admin yoki student topish
        admin = None
        student = None
        
        if admin_id:
            try:
                admin = User.objects.get(id=admin_id, role='admin')
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {"admin_id": "Admin topilmadi"}
                )
            student = sender
        else:
            try:
                student = User.objects.get(id=student_id, role='student')
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {"student_id": "Student topilmadi"}
                )
            admin = sender
        
        # Xabar yaratish
        message = Message.objects.create(
            sender=sender,
            admin=admin,
            student=student,
            **validated_data
        )
        
        return message


class UnreadCountSerializer(serializers.Serializer):
    """
    O'qilmagan xabarlar sonini qaytarish uchun serializer
    """
    unread_count = serializers.IntegerField()


class ConversationUserSerializer(serializers.Serializer):
    image_qrkod = serializers.SerializerMethodField()

    """
    Conversation users serializer o'qilmagan xabar soni bilan
    """
    id = serializers.UUIDField()
    uuid = serializers.CharField()
    username = serializers.CharField()
    phone_number = serializers.CharField()
    role = serializers.CharField()
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    image_qrkod = serializers.CharField()
    tg_username = serializers.CharField(required=False, allow_blank=True)
    level = serializers.CharField(required=False, allow_blank=True)
    course = serializers.CharField(required=False, allow_blank=True)
    direction = serializers.CharField(required=False, allow_blank=True)
    coins = serializers.IntegerField(required=False)
    photo = serializers.SerializerMethodField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    unread_message_count = serializers.SerializerMethodField()
    
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


    
    def get_photo(self, obj):
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None
    
    def get_unread_message_count(self, obj):
        """
        User uchun o'qilmagan xabarlar sonini hisoblash
        """
        current_user = self.context.get('request').user
        if not current_user or not current_user.is_authenticated:
            return 0
        
        unread_count = Message.objects.filter(
            Q(admin=current_user, student=obj, is_read=False) |
            Q(student=current_user, admin=obj, is_read=False) |
            Q(admin=current_user, sender=obj, is_read=False) |
            Q(student=current_user, sender=obj, is_read=False)
        ).exclude(sender=current_user).count()
        return unread_count


class UnreadNotificationSerializer(serializers.ModelSerializer):
    """
    O'qilmagan xabarlar notification uchun serializer
    """
    sender_id = serializers.IntegerField(source='sender.id')
    sender_name = serializers.SerializerMethodField()
    sender_photo = serializers.SerializerMethodField()
    sender_role = serializers.CharField(source='sender.role')
    message = serializers.CharField(source='text')
    
    class Meta:
        model = Message
        fields = [
            'id',
            'sender_id',
            'sender_name',
            'sender_photo',
            'sender_role',
            'message',
            'created_at',
            'is_read',
        ]
    
    def get_sender_name(self, obj):
        """Yuboruvchi to'liq ismini qaytaradi"""
        return f"{obj.sender.first_name} {obj.sender.last_name}".strip()
    
    def get_sender_photo(self, obj):
        """Yuboruvchi fotosuratini qaytaradi"""
        if obj.sender.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.sender.photo.url)
            return obj.sender.photo.url
        return None
