from rest_framework import serializers
from .models import Group
from apps.users.serializers import UserSerializer


class GroupSerializer(serializers.ModelSerializer):
    # GET uchun o'quvchilarning to'liq ma'lumotlarini qaytaradi
    students = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "smena",
            "start_time",
            "students",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
    
    def get_students(self, obj):
        """O'quvchilarning to'liq ma'lumotlarini qaytaradi"""
        students = obj.students.all()
        return UserSerializer(students, many=True, context=self.context).data

