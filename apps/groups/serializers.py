from rest_framework import serializers
from .models import Group


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "smena",
            "start_time",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
