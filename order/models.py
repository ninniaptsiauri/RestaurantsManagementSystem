from django.db import models
from user.models import Customer
from restaurant.models import Restaurant, MenuItem
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver




class ShoppingCart(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='shopping_cart', null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('customer', 'restaurant')
        db_table = 'shopping_cart'

    def __str__(self):
        return f'Shopping cart for {self.customer.name} at {self.restaurant.name}'
    
    def get_total_price(self):
        total_price = sum(item.menu_item.price * item.quantity for item in self.items.all())
        return total_price
    

class ShoppingCartItem(models.Model):
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    add_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'shopping_cart_item'

    def __str__(self):
        return f'{self.menu_item.name} x {self.quantity} in {self.cart}'
    
    def get_item_price(self):
        return self.menu_item.price * self.quantity
    
    
    
    


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order'


    def calculate_total_price(self):
        total = 0
        for item in self.order_items.all():
            total += item.price * item.quantity
        self.total_price = total
        self.save()
    


    def __str__(self):
        return f'Order {self.pk} by {self.customer.name}'

    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'order_item'

    def __str__(self):
        return f'{self.menu_item.name} x {self.quantity} in {self.order}'
    

    @property
    def get_total_price(self):
        return self.quantity * self.price

