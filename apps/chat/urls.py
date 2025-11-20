from django.urls import path
from .views import ConversationListView, MessageListView, MessageCreateView, UnreadMessageCountView, ReadMessageView

urlpatterns = [
    path('', MessageListView.as_view(), name='message_list'),
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('messages/', MessageListView.as_view(), name='message-list'),
    path('unread-count/', UnreadMessageCountView.as_view(), name='unread-count'),
    path('mark-read/', ReadMessageView.as_view(), name='mark-read'),
    path('add/', MessageCreateView.as_view(), name='message-create'),
]
