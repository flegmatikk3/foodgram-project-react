from django.contrib import admin

from .models import User


@admin.register(User)
class AdminUser(admin.ModelAdmin):
    list_display = (
        'id', 'email',
        'username',
        'first_name',
        'last_name'
    )
    list_filter = ('first_name', 'email')
    search_fields = ('email', 'username')
