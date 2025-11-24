from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, MessagesListView

router = DefaultRouter()
router.register(r'', MessageViewSet, basename='messages')

urlpatterns = [
    path('', include(router.urls)), 
    path('ms/user_message/', MessagesListView.as_view(), name='message-list'), 
    path('ms/user_message/<int:pk>/', MessagesListView.as_view(), name='message-detail'), 
]
