from django.db import models
from user.models import Customer
from restaurant.models import Restaurant, Table
from django.db.models import Q
from django.utils import timezone




class Reservation(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='reservations')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reservations')
    reservation_date = models.DateTimeField()
    reservation_end_time = models.DateTimeField()
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='reservations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_cancelled = models.BooleanField(default=False)
    special_requests = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'reservation'
    
    def __str__(self):
        return f"Reservation for {self.customer.name} at {self.restaurant.name}"
    
    def check_availability(self):
        existing_reservations = Reservation.objects.filter(
            table=self.table,
            is_cancelled=False
        ).filter(
            Q(reservation_date__lt=self.reservation_end_time) & 
            Q(reservation_end_time__gt=self.reservation_date)
        ).exclude(pk=self.pk)

        return not existing_reservations.exists()
        

    

    @property
    def is_future(self):
        return self.reservation_date > timezone.now()
