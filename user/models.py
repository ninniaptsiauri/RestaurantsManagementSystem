from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission



class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('restaurant_owner', 'Restaurant Owner'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=40)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True)


    groups = models.ManyToManyField(
        Group, 
        verbose_name='groups', 
        blank=True,
        related_name='custom_user_set', 
        related_query_name='custom_user'
    )
    user_permissions= models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user'
        )
    
                                    
    
    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.username



class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'customer'

    


class RestaurantOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    restaurant_name = models.CharField(max_length=150)
    restaurant_address = models.CharField(max_length=200)
    description = models.TextField()
    
    class Meta:
        db_table = 'restaurant_owner'



