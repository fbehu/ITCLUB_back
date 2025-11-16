from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'admin', 'student', 'created_at']
    list_filter = ['created_at', 'admin', 'student']
    search_fields = ['text', 'sender__username', 'admin__username', 'student__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Xabar ma\'lumotlari', {
            'fields': ('id', 'text', 'file')
        }),
        ('Ishtirokchilar', {
            'fields': ('sender', 'admin', 'student')
        }),
        ('Vaqtlar', {
            'fields': ('created_at', 'updated_at')
        }),
    )
