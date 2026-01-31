from rest_framework import serializers
from .models import Attendance
from apps.groups.models import Group
from apps.users.models import User
from django.utils import timezone

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class StudentListSerializer(serializers.ModelSerializer):
    """Guruh bo'yicha o'quvchilarni ko'rsatish uchun"""
    attendance_status = serializers.SerializerMethodField()
    attendance_reason = serializers.SerializerMethodField()
    attendance_coins = serializers.SerializerMethodField()
    is_attendance_locked = serializers.SerializerMethodField()
    
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
            "attendance_status",
            "attendance_reason",
            "attendance_coins",
            "is_attendance_locked",
        ]
    
    def get_attendance_status(self, obj):
        """O'sha kun uchun davomat statusini qaytaradi"""
        date = self.context.get('date')
        if date:
            attendance = Attendance.objects.filter(user=obj, date=date).first()
            return attendance.status if attendance else None
        return None
    
    def get_attendance_reason(self, obj):
        """O'sha kun uchun davomat sababini qaytaradi"""
        date = self.context.get('date')
        if date:
            attendance = Attendance.objects.filter(user=obj, date=date).first()
            return attendance.reason if attendance else None
        return None
    
    def get_attendance_coins(self, obj):
        """O'sha kun uchun berilgan ballni qaytaradi"""
        date = self.context.get('date')
        if date:
            attendance = Attendance.objects.filter(user=obj, date=date).first()
            return attendance.coins if attendance else 0
        return 0
    
    def get_is_attendance_locked(self, obj):
        """O'sha kun uchun davomat qulflab qo'yilganmi tekshiradi"""
        date = self.context.get('date')
        if date:
            today = timezone.now().date()
            
            # O'tmish sana bo'lsa - qulflab qo'yish
            if date < today:
                return True
            
            # Davomat allaqachon qo'shilgan bo'lsa - qulflab qo'yish
            attendance = Attendance.objects.filter(user=obj, date=date).first()
            if attendance:
                return True
            
            # Bugungi kun va kelajak - o'chirib qo'yish (davomat qo'shish mumkin)
            return False
        
        return False

class AttendanceSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Attendance
        fields = ['id', 'group', 'user', 'date', 'status', 'reason', 'coins']
        read_only_fields = ['id']

    def validate(self, data):
        # O'tmish sana bo'lsa - xato qaytarish
        if 'date' in data and data['date'] < timezone.now().date():
            raise serializers.ValidationError("Attendance cannot be recorded for past dates. O'tmish sanalarda davomat qo'shib bo'lmaydi.")
        return data
    
    def to_representation(self, instance):
        """Response'da group'ni serialized ko'rinishda qaytarish"""
        ret = super().to_representation(instance)
        ret['group'] = GroupSerializer(instance.group).data
        return ret


class BulkAttendanceSerializer(serializers.Serializer):
    """Bitta so'rovda ko'p studentlarni davomat qilish uchun"""
    group_id = serializers.IntegerField(required=True)
    date = serializers.DateField(required=True, format='%Y-%m-%d')
    students = serializers.ListField(required=True)
    
    def validate(self, data):
        # O'tmish sana bo'lsa - xato qaytarish
        if data['date'] < timezone.now().date():
            raise serializers.ValidationError(
                "O'tmish sanalarda davomat qo'shib bo'lmaydi. "
                f"Bugun: {timezone.now().date()}"
            )
        
        # Group mavjudligini tekshirish
        try:
            Group.objects.get(id=data['group_id'])
        except Group.DoesNotExist:
            raise serializers.ValidationError("Bunday guruh topilmadi.")
        
        # Students arrayni tekshirish
        if not data['students']:
            raise serializers.ValidationError("Students ro'yxati bo'sh bo'lishi mumkin emas.")
        
        return data