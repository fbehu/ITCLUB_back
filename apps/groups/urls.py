from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupsViewSet

router = DefaultRouter()
router.register(r'', GroupsViewSet, basename='groups')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/students/', GroupsViewSet.as_view({'get': 'students', 'post': 'students'}), name='group-students'),
]
# students endpoint GET va POST uchun maxsus URL router orqali yo'naltiriladi
