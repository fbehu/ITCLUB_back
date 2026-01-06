from django.contrib import admin
from .models import Group

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'smena', 'start_time', 'teacher', 'created_at', 'updated_at')
    search_fields = ('name', 'smena', 'teacher__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('students',)
