from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Customer, RestaurantOwner

class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username',  'email', 'phone_number']



class CustomerAddressAddForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['address']



class RestaurantOwnerRegistrationForm(UserCreationForm):
    
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'phone_number', 'email', ]



class RestaurantOwnerInfoForm(forms.ModelForm):
    class Meta:
        model = RestaurantOwner
        fields = ['restaurant_name', 'restaurant_address', 'description']
        



class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']



class CustomerUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['address']




class RestaurantOwnerUpdateForm(forms.ModelForm):
    class Meta:
        model = RestaurantOwner
        fields = ['restaurant_name', 'restaurant_address', 'description']