from django.urls import path
from .views import (
    LoginView, ProfileView, LogoutView, ChangePasswordView, 
    TeacherOnlyUserListView, AdminUserUpdateView, UserStatisticsAPIView, 
    AdminChangeUserPasswordAPIView, AdminCreateUserAPIView,
    AdminCheckUserAPIView, # RegisterView, 
)
urlpatterns = [
    path("users/", TeacherOnlyUserListView.as_view(), name="user-list"),
    path("add/", AdminCreateUserAPIView.as_view(), name="admin-create-user"),
    path("check-users/", AdminCheckUserAPIView.as_view(), name="admin-check-user"),
    path("users/<uuid:pk>/", AdminUserUpdateView.as_view(), name="user-detail"),
    path("users/<uuid:user_id>/change-password/", AdminChangeUserPasswordAPIView.as_view(), name="admin-change-user-password"),
    # path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", ProfileView.as_view(), name="profile"),
    path("logout/", LogoutView.as_view(), name="logout"),

    # Password
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),

    # Statistics
    path("statistics/", UserStatisticsAPIView.as_view(), name="user-statistics"),
]
