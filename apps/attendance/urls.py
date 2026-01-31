from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceViewSet

router = DefaultRouter()
router.register(r'', AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('', include(router.urls)),
    path('group/<int:group_id>/<str:date>/', AttendanceViewSet.as_view({'get': 'get_group_students_attendance'}), name='attendance-by-group-date'),
]