from rest_framework import serializers
from .models import Group


class GroupSerializer(serializers.ModelSerializer):
    # return list of student UUIDs
    students = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

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
