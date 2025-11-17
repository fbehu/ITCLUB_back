from django.urls import path
from .views import MessageListView, MessageCreateView

urlpatterns = [
    path('', MessageListView.as_view(), name='message-list'),
    path('add/', MessageCreateView.as_view(), name='message-create'),
]
