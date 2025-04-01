from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Customer, RestaurantOwner
from django.contrib.auth.models import Group

class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username',  'email', 'phone_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            customer_group = Group.objects.get(name='customer')
            user.groups.add(customer_group)
        return user
    


class CustomerAddressAddForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['address']



class RestaurantOwnerRegistrationForm(UserCreationForm):
    
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'phone_number', 'email', ]

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            restaurant_owner_group = Group.objects.get(name='restaurant_owner')
            user.groups.add(restaurant_owner_group)
        return user
    




class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']



class CustomerUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['address']




