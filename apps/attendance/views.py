from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Attendance
from .serializers import AttendanceSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.groups.models import Group

class AttendanceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, group_id, date):
        group = get_object_or_404(Group, id=group_id)
        attendance_date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
        attendance_record = Attendance.objects.filter(group=group, date=attendance_date).first()

        if attendance_record:
            serializer = AttendanceSerializer(attendance_record)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Attendance record not found."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        serializer = AttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)