from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import ProfileSerializer, ChangePasswordSerializer, UserStatisticsSerializer

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'detail': "Parol muvaffaqiyatli o'zgartirildi."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserStatisticsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserStatisticsSerializer(request.user)
        return Response(serializer.data)


class AttendanceStatisticsAPIView(APIView):
    """
    Foydalanuvchining davomat statistikasi
    GET /api/profile/attendance/?year=2026&month=1
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from apps.attendance.models import Attendance
        from datetime import datetime
        from django.db.models import Q, Count
        
        user = request.user
        year = request.query_params.get('year', datetime.now().year)
        month = request.query_params.get('month', datetime.now().month)
        
        try:
            year = int(year)
            month = int(month)
        except (ValueError, TypeError):
            return Response(
                {"detail": "Year va month raqam bo'lishi kerak."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # O'sha oy uchun davomat ma'lumotlarini olish
        attendances = Attendance.objects.filter(
            user=user,
            date__year=year,
            date__month=month
        ).order_by('date')
        
        if not attendances.exists():
            return Response({
                "year": year,
                "month": month,
                "message": "Bu oy uchun davomat ma'lumoti yo'q",
                "summary": {
                    "total_classes": 0,
                    "present_count": 0,
                    "absent_count": 0,
                    "excuse_count": 0,
                    "attendance_percentage": 0
                },
                "daily_attendance": []
            }, status=status.HTTP_200_OK)
        
        # Statistika hisoblash
        total_count = attendances.count()
        present_count = attendances.filter(status='present').count()
        absent_count = attendances.filter(status='absent').count()
        excuse_count = attendances.filter(status='excuse').count()
        attendance_percentage = round((present_count / total_count * 100), 2) if total_count > 0 else 0
        
        # Kunlik davomat ma'lumotlari
        daily_attendance = []
        for attendance in attendances:
            daily_attendance.append({
                "date": attendance.date,
                "day_name": attendance.date.strftime("%A"),  # Haftaning kunini qaytaradi
                "group_name": attendance.group.name if attendance.group else "",
                "group_id": attendance.group.id if attendance.group else "",
                "status": attendance.status,
                "reason": attendance.reason if attendance.status == 'excuse' else None,
                "coins": attendance.coins,
            })
        
        return Response({
            "year": year,
            "month": month,
            "summary": {
                "total_classes": total_count,
                "present_count": present_count,
                "absent_count": absent_count,
                "excuse_count": excuse_count,
                "attendance_percentage": attendance_percentage
            },
            "daily_attendance": daily_attendance
        }, status=status.HTTP_200_OK)
