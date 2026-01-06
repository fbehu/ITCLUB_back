from django.urls import path, include

urlpatterns = [
    path("users/", include("apps.users.urls")),
    path("message/", include("apps.chat.urls")),
    path("messages/", include("apps.message.urls")),
    path("groups/", include("apps.groups.urls")),
    path("attendance/", include("apps.attendance.urls")),
    path("news/", include("apps.news.urls")),
]
