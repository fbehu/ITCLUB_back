from rest_framework import serializers
from .models import Message
from apps.users.models import User


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
