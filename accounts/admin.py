from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'is_admin_staff', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    list_filter = ('is_admin_staff',)
