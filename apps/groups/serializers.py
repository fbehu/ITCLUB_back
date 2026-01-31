from rest_framework import serializers
from .models import Group
from apps.users.serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class TeacherBriefSerializer(serializers.ModelSerializer):
    """O'qituvchining qisqacha ma'lumotlari"""
    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'username',
            'phone_number',
            'photo',
            'level',
            'role'
        ]


class GroupSerializer(serializers.ModelSerializer):
    # GET uchun o'quvchilarning ID larini qaytaradi
    students = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    # teacher display uchun - o'qish uchun to'liq ma'lumot
    teacher_display = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "start_time",
            "end_time",
            "class_days",
            "teacher",
            "teacher_display",
            "student_count",
            "students",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "teacher_display"]
    
    def get_student_count(self, obj):
        """Guruhda nechta o'quvchi borligini qaytaradi"""
        return obj.students.count()
    
    def get_students(self, obj):
        """O'quvchilarning ID larini qaytaradi"""
        students = obj.students.all()
        return [str(student.id) for student in students]
    
    def get_teacher_display(self, obj):
        """O'qituvchining qisqacha ma'lumotlarini qaytaradi"""
        if obj.teacher:
            return TeacherBriefSerializer(obj.teacher, context=self.context).data
        return None
    
    def to_representation(self, instance):
        """GET javobida teacher_display o'rniga teacher qaytaradi"""
        ret = super().to_representation(instance)
        # teacher_display ma'lumotlarini teacher maydoniga ko'chirish
        if 'teacher_display' in ret:
            ret['teacher'] = ret.pop('teacher_display')
        return ret
    
    def to_internal_value(self, data):
        """POST/PUT so'rovlarida teacher UUID qabul qiladi"""
        if 'teacher' in data and isinstance(data['teacher'], str):
            try:
                user = User.objects.get(id=data['teacher'])
                data['teacher'] = user.id
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {"teacher": f"ID {data['teacher']} bo'lgan o'qituvchi topilmadi"}
                )
            except Exception as e:
                raise serializers.ValidationError(
                    {"teacher": f"Noto'g'ri teacher UUID: {str(e)}"}
                )
        
        return super().to_internal_value(data)