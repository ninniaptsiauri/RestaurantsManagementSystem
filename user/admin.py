from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('id', 'email', 'username', 'first_name', 'last_name', 'is_staff', 'role')
    search_fields = ('email', 'username')


admin.site.register(User, CustomUserAdmin)