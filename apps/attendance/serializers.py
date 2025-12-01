from rest_framework import serializers
from .models import Attendance, Group

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class AttendanceSerializer(serializers.ModelSerializer):
    group = GroupSerializer()

    class Meta:
        model = Attendance
        fields = ['id', 'group', 'date', 'status']
        read_only_fields = ['id'] 

    def validate(self, data):
        if 'date' in data and data['date'] < timezone.now().date():
            raise serializers.ValidationError("Attendance cannot be recorded for past dates.")
        return data