from django.test import TestCase
from .models import Group, Attendance
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

class AttendanceAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.group = Group.objects.create(name="Test Group")
        self.attendance_date = timezone.now().date()
        self.attendance = Attendance.objects.create(group=self.group, date=self.attendance_date, status='present')

    def test_get_attendance_status_existing_group(self):
        response = self.client.get(f'/attendance/{self.group.id}/attendance/?date={self.attendance_date}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'present')

    def test_get_attendance_status_non_existing_group(self):
        response = self.client.get('/attendance/999/attendance/?date={self.attendance_date}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_attendance_existing_group(self):
        response = self.client.post(f'/attendance/{self.group.id}/attendance/', {'date': self.attendance_date, 'status': 'absent'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Attendance.objects.last().status, 'absent')

    def test_post_attendance_non_existing_group(self):
        response = self.client.post('/attendance/999/attendance/', {'date': self.attendance_date, 'status': 'present'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)