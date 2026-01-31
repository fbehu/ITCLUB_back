from django.urls import path
from .views import ProfileView, ChangePasswordView, UserStatisticsAPIView, AttendanceStatisticsAPIView

urlpatterns = [
    path("me/", ProfileView.as_view(), name="profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("statistics/", UserStatisticsAPIView.as_view(), name="user-statistics"),
    path("attendance/", AttendanceStatisticsAPIView.as_view(), name="attendance-statistics"),
]
