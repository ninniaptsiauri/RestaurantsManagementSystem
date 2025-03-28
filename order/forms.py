from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import ShoppingCart, ShoppingCartItem, Order, OrderItem

class ShoppingCartForm(forms.ModelForm):
    class Meta:
        model = ShoppingCart
        fields = ['restaurant']

    def __init__(self, customer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.customer = customer
            

class ShoppingCartItemForm(forms.ModelForm):
    class Meta:
        model = ShoppingCartItem
        fields = ['menu_item', 'quantity' ]

    def __init__(self, customer, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.customer = customer
       

    
class OrderAddressForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['address']
        widgets = {
            'address': forms.TextInput(attrs= {'class': 'form-control'})
        }
        

    

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = '__all__'

    
    def __init__(self, order, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.order = order
        
