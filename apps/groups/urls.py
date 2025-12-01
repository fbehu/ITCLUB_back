from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupsViewSet

router = DefaultRouter()
router.register(r'', GroupsViewSet, basename='groups')

urlpatterns = [
    path('', include(router.urls)),
]
