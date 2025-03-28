from django.db import models
from user.models import User

class RestaurantCategory(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False, unique=True)
    
    class Meta:
        db_table = 'restaurant_category'

    def __str__(self):
        return self.name
    
    

class Restaurant(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    address = models.CharField(max_length=150, null=False, blank=False)
    category = models.ForeignKey(RestaurantCategory, on_delete=models.CASCADE, related_name='restaurants')
    description = models.TextField()
    opening_hour = models.TimeField()
    closing_hour = models.TimeField()
    phone_number = models.CharField(max_length=20, null=False, blank=False, help_text='Format: +995 512 345 678 or +995 32 2123456') 
    restaurant_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurants')
    add_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='restaurant_images/', null=True, blank=True)

    class Meta:
        db_table = 'restaurant'

    def __str__(self):
        return self.name
    


class MenuCategory(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_categories')
    name = models.CharField(max_length=50, null=False, blank=False)

    class Meta:
        db_table = 'menu_category'

    def __str__(self):
        return self.name
        


class MenuItem(models.Model):
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=150, null=False, blank=False)
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='menu_item_images/', null=True, blank=True)
    add_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'menu_item'

    def __str__(self):
        return self.name
        
    
    
        
class Table(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tables')
    capacity = models.PositiveIntegerField()
    table_number = models.CharField(max_length=10, help_text='e.g., 1A, 2B, 3C, ...')
    location = models.CharField(max_length=100, null=True, blank=True)
    add_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'table'

    def __str__(self):
        return f'{self.capacity} person table in {self.restaurant.name}'
    


    