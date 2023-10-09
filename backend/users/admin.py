from django.contrib import admin
from .models import User, Follow

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


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'author')
    list_filter = ('author',)
    search_fields = ('follower',)
