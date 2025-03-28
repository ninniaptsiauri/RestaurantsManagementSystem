from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from . models import Restaurant, MenuCategory, MenuItem, Table
import re


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'address', 'category', 'description', 'opening_hour', 'closing_hour', 'phone_number', 'image']

    
        widgets = {
            'opening_hour': forms.TimeInput(attrs={'type': 'time'}),
            'closing_hour': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        phone_number = re.sub(r'\D', '', phone_number)
        return phone_number
    

class MenuCategoryForm(forms.ModelForm):
    class Meta:
        model = MenuCategory
        fields = ['restaurant', 'name']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['restaurant'].queryset = Restaurant.objects.filter(restaurant_owner=self.user)
    
    def clean(self):
        cleaned_data = super().clean()
        restaurant = cleaned_data.get('restaurant')
        if restaurant and restaurant.restaurant_owner == self.user:
            return cleaned_data
            

            

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['category', 'name', 'description', 'price', 'image']

    def __init__(self, menu_category, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu_category = menu_category
        self.fields['category'].queryset = MenuCategory.objects.filter(restaurant=self.menu_category.restaurant)


        def clean(self):
            cleaned_data = super().clean()
            menu_category = cleaned_data.get('category')
            if menu_category and menu_category.restaurant == self.menu_category.restaurant:
                return cleaned_data
                


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['restaurant', 'capacity', 'table_number', 'location']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['restaurant'].queryset = Restaurant.objects.filter(restaurant_owner=self.user)

    def clean(self):
        cleaned_data = super().clean()
        restaurant = cleaned_data.get('restaurant')
        if restaurant and restaurant.restaurant_owner == self.user:
            return cleaned_data