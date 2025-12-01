from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Attendance
from .serializers import AttendanceSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.groups.models import Group
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
            return Attendance.objects.filter(group=group, date=attendance_date, user=user).exists()
        except Exception:
            # Can't determine; assume not attended so the API remains permissive,
            # client can still attempt to create and server-side validation should enforce.
            return False

    def list(self, request):
        """
        GET /api/attendance/?group_id=1&date=2025-12-01
        Returns {"can_attend": True} if the requesting user has not yet attended for that group/date,
        otherwise {"can_attend": False, "detail": "..."}.
        """
        group_id = request.query_params.get("group_id")
        date_str = request.query_params.get("date")

        if not group_id or not date_str:
            return Response({"detail": "group_id and date query params are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            group = get_object_or_404(Group, id=group_id)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid group_id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            attendance_date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        attendance_record = Attendance.objects.filter(group=group, date=attendance_date).first()
        already = self._user_already_attended(attendance_record, group, attendance_date, request.user)

        if already:
            return Response({"can_attend": False, "detail": "You have already attended on this date."}, status=status.HTTP_200_OK)
        else:
            return Response({"can_attend": True}, status=status.HTTP_200_OK)

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
        # Quick duplicate check before creating: if the user already attended for the provided group/date reject.
        # We attempt to read group/date from the incoming data; serializer validation remains authoritative.
        group_val = request.data.get("group") or request.data.get("group_id")
        date_val = request.data.get("date")

        if group_val and date_val:
            try:
                group = Group.objects.get(id=group_val)
                attendance_date = timezone.datetime.strptime(date_val, "%Y-%m-%d").date()
                attendance_record = Attendance.objects.filter(group=group, date=attendance_date).first()
                if self._user_already_attended(attendance_record, group, attendance_date, request.user):
                    return Response({"detail": "You have already attended on this date."}, status=status.HTTP_400_BAD_REQUEST)
            except (Group.DoesNotExist, ValueError, TypeError):
                # let serializer handle invalid group/date if present
                pass

        serializer = AttendanceSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)