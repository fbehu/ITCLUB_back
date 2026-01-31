from django.urls import path
from .views import (
    TeacherOnlyUserListView, AdminUserUpdateView, 
    AdminChangeUserPasswordAPIView, AdminCreateUserAPIView,
    AdminCheckUserAPIView, AdminsListView,
)

urlpatterns = [
    path("", TeacherOnlyUserListView.as_view(), name="user-list"),
    path("admins/", AdminsListView.as_view(), name="admin-list"),
    path("add/", AdminCreateUserAPIView.as_view(), name="admin-create-user"),
    path("check/", AdminCheckUserAPIView.as_view(), name="admin-check-user"),
    path("<uuid:pk>/", AdminUserUpdateView.as_view(), name="user-detail"),
    path("<uuid:user_id>/change-password/", AdminChangeUserPasswordAPIView.as_view(), name="admin-change-user-password"),
]
