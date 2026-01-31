from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Attendance
from .serializers import (
    AttendanceSerializer, 
    StudentListSerializer,
    BulkAttendanceSerializer
)
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from apps.groups.models import Group
from apps.users.models import User
from django.core.exceptions import ObjectDoesNotExist

class AttendanceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def _user_already_attended(self, attendance_record, group, attendance_date, user):
        """
        Try several common Attendance model shapes:
        - A per-date Attendance with a ManyToMany field (common names checked)
        - A per-user Attendance row (Attendance has a FK 'user' or similar)
        - Fallback: check for rows filtered by group/date/user
        """
        # If no attendance record exists, user hasn't attended
        if not attendance_record:
            return False

        # Try common many-to-many field names
        for m2m_name in ("attendees", "present", "users", "members", "students"):
            m2m = getattr(attendance_record, m2m_name, None)
            if m2m is not None:
                try:
                    return m2m.filter(id=user.id).exists()
                except Exception:
                    # if attribute exists but isn't a manager, skip
                    continue

        # Try common single-user FK field names
        for fk_name in ("user", "student", "member", "created_by"):
            fk = getattr(attendance_record, fk_name, None)
            if fk is not None:
                try:
                    return fk.id == user.id
                except Exception:
                    continue

        # Last resort: check for a per-user Attendance row
        try:
            return Attendance.objects.filter(group_id=group.id if isinstance(group, Group) else group, date=attendance_date, user=user).exists()
        except Exception:
            # Can't determine; assume not attended so the API remains permissive,
            # client can still attempt to create and server-side validation should enforce.
            return False

    def _resolve_group(self, group_param):
        """
        Accept a Group instance, an integer id (or numeric string), or a name/title/slug string.
        Return a Group instance or None if not found/invalid.
        """
        if not group_param:
            return None
        if isinstance(group_param, Group):
            return group_param
        # try by id
        try:
            return Group.objects.get(id=int(group_param))
        except (ValueError, TypeError, Group.DoesNotExist):
            pass
        # try common name fields
        for field in ("name", "title", "slug"):
            try:
                kwargs = {field: group_param}
                return Group.objects.get(**kwargs)
            except Group.DoesNotExist:
                continue
        return None

    def list(self, request):
        """
        GET /api/attendance/?group_id=1&date=2025-12-01
        Returns {"can_attend": True} if the requesting user has not yet attended for that group/date,
        otherwise {"can_attend": False, "detail": "..."}.
        """
        group_param = request.query_params.get("group_id")
        date_str = request.query_params.get("date")

        if not group_param or not date_str:
            return Response({"detail": "group_id and date query params are required."}, status=status.HTTP_400_BAD_REQUEST)

        # resolve group_param into a Group instance (defensive against raw strings)
        group = self._resolve_group(group_param)
        if group is None:
            return Response({"detail": "Invalid group identifier."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            attendance_date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # use group_id to avoid passing non-Group values into FK lookups
        attendance_record = Attendance.objects.filter(group_id=group.id if isinstance(group, Group) else group, date=attendance_date).first()
        already = self._user_already_attended(attendance_record, group, attendance_date, request.user)

        if already:
            return Response({"can_attend": False, "detail": "You have already attended on this date."}, status=status.HTTP_200_OK)
        else:
            return Response({"can_attend": True}, status=status.HTTP_200_OK)

    def get_group_students_attendance(self, request, group_id, date):
        """
        GET /api/attendance/group/{group_id}/{date}/
        Guruh bo'yicha o'quvchilarni davomat ma'lumotlari bilan qaytaradi.
        
        Qulflab qo'yish qoidasi:
        - Agar sana o'tmish bo'lsa: qulflab qo'yadi (is_locked: true)
        - Agar sana o'tmish bo'lsa va hamma o'quvchi davomat qo'shilgan bo'lsa: qulflab qo'yadi
        - Agar sana bugungi kun yoki kelajak bo'lsa va davomat qo'shilmagan bo'lsa: o'chirib qo'yadi (is_locked: false)
        """
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({"detail": "Group not found."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            attendance_date = timezone.datetime.strptime(date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        
        today = timezone.now().date()
        
        # Guruhdagi barcha o'quvchilarni olish
        students = group.students.all()
        
        # Serializer'ga context qo'shish
        serializer = StudentListSerializer(
            students,
            many=True,
            context={'date': attendance_date}
        )
        
        # is_locked statusini aniqlash
        # Agar o'tmish sana bo'lsa - qulflab qo'yish
        if attendance_date < today:
            is_locked = True
        else:
            # Bugungi kun yoki kelajak - hamma o'quvchi uchun davomat qo'shilgan bo'lsa qulflab qo'yish
            all_attended = all(student['is_attendance_locked'] for student in serializer.data)
            is_locked = all_attended
        
        return Response({
            "count": students.count(),
            "date": attendance_date,
            "is_locked": is_locked,
            "can_edit": not is_locked,
            "students": serializer.data
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, group_id, date):
        group = get_object_or_404(Group, id=group_id)
        attendance_date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
        attendance_record = Attendance.objects.filter(group_id=group.id if isinstance(group, Group) else group, date=attendance_date).first()

        if attendance_record:
            serializer = AttendanceSerializer(attendance_record)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Attendance record not found."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        """
        Yangi davomat qo'shish - bitta so'rovda ko'p studentlarni qabul qiladi.
        
        Request format:
        {
            "group_id": 1,
            "date": "2026-01-31",
            "students": [
                {
                    "id": "user_id_1",
                    "status": "present",  // 'present' (kelgan), 'absent' (kelmagan), 'excuse' (sababli)
                    "reason": "Kasal edi",  // optional, faqat 'excuse' bo'lsa kerak
                    "coins": 50  // optional, max 100
                },
                {
                    "id": "user_id_2",
                    "status": "absent",
                    "coins": 0
                }
            ]
        }
        """
        serializer = BulkAttendanceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        group_id = serializer.validated_data['group_id']
        attendance_date = serializer.validated_data['date']
        students_data = serializer.validated_data['students']
        
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response(
                {"detail": "Guruh topilmadi."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        results = {
            "success": [],
            "errors": [],
            "total_coins_added": 0
        }
        
        # Transaction ichida barchasini saqlaymiz
        with transaction.atomic():
            for student_data in students_data:
                user_id = student_data.get('id')
                status_val = student_data.get('status')
                reason = student_data.get('reason', '')
                coins = int(student_data.get('coins', 0))
                
                # Validacija
                if not user_id or not status_val:
                    results['errors'].append({
                        'student_id': user_id,
                        'detail': 'id va status majburiy.'
                    })
                    continue
                
                if status_val not in ['present', 'absent', 'excuse']:
                    results['errors'].append({
                        'student_id': user_id,
                        'detail': f"Status '{status_val}' noto'g'ri. Qabul qilingan qiymatlar: present, absent, excuse"
                    })
                    continue
                
                # Sababli bo'lsa, sababni tekshirish
                if status_val == 'excuse':
                    if not reason or reason.strip() == '':
                        results['errors'].append({
                            'student_id': user_id,
                            'detail': "Sababli bo'lsa, 'reason' majburiy."
                        })
                        continue
                else:
                    # Kelgan yoki kelmagan bo'lsa, reason bo'sh bo'lishi kerak
                    reason = ''
                
                # Ballni tekshirish (max 100)
                if coins < 0 or coins > 100:
                    results['errors'].append({
                        'student_id': user_id,
                        'detail': f"Balllar 0 dan 100 gacha bo'lishi kerak, berilgan: {coins}"
                    })
                    continue
                
                # User mavjudligini tekshirish
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    results['errors'].append({
                        'student_id': user_id,
                        'detail': "Foydalanuvchi topilmadi."
                    })
                    continue
                
                # O'sha kun uchun davomat allaqachon bo'lganmi tekshirish
                existing_attendance = Attendance.objects.filter(
                    group_id=group_id,
                    user_id=user_id,
                    date=attendance_date
                ).first()
                
                if existing_attendance:
                    results['errors'].append({
                        'student_id': user_id,
                        'detail': f"Bu kun ({attendance_date}) uchun davomat allaqachon qayd qilingan.",
                        'existing_record_id': existing_attendance.id
                    })
                    continue
                
                # Davomat qo'shish
                try:
                    attendance = Attendance.objects.create(
                        group_id=group_id,
                        user_id=user_id,
                        date=attendance_date,
                        status=status_val,
                        reason=reason if status_val == 'excuse' else '',
                        coins=coins
                    )
                    
                    # Agar 'kelgan' bo'lsa, balllar qo'shish
                    if status_val == 'present' and coins > 0:
                        user.coins = (user.coins or 0) + coins
                        user.save()
                        results['total_coins_added'] += coins
                    
                    results['success'].append({
                        'student_id': user_id,
                        'username': user.username,
                        'status': status_val,
                        'coins_added': coins if status_val == 'present' else 0,
                        'attendance_id': attendance.id
                    })
                except Exception as e:
                    results['errors'].append({
                        'student_id': user_id,
                        'detail': f"Xatolik: {str(e)}"
                    })
        
        return Response(results, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """
        Update'ni yoplab qo'yish - davomat qo'shilgandan keyin o'zgartirib bo'lmaydi.
        """
        return Response(
            {"detail": "Davomat qo'shilgandan keyin uni o'zgartirib bo'lmaydi. Agar o'zgartirish kerak bo'lsa, avval o'chirib keyin yangi qo'shishingiz kerak."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request, pk=None):
        """
        Partial update'ni yoplab qo'yish.
        """
        return Response(
            {"detail": "Davomat qo'shilgandan keyin uni o'zgartirib bo'lmaydi. Agar o'zgartirish kerak bo'lsa, avval o'chirib keyin yangi qo'shishingiz kerak."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )