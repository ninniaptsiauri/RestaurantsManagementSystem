from django import forms
from .models import Reservation


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['reservation_date', 'reservation_end_time', 'special_requests', 'restaurant', 'table']

        widgets = {
            'reservation_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'reservation_end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

