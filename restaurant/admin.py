from django.contrib import admin
from . models import Restaurant


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'phone_number', 'add_time')
    ordering = ('-add_time',)
    search_fields = ('name', 'category__name')
    list_filter =('category',)


admin.site.register(Restaurant, RestaurantAdmin)