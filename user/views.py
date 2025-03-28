from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from user.models import User, Customer, RestaurantOwner
from restaurant.models import Restaurant, MenuCategory
from .forms import CustomerRegistrationForm, RestaurantOwnerRegistrationForm, CustomerAddressAddForm, RestaurantOwnerInfoForm
from .forms import UserUpdateForm, RestaurantOwnerUpdateForm, CustomerUpdateForm
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings
from django.db import OperationalError
import logging
from django.contrib import messages
from .utils import validate_profile_update






logger = logging.getLogger(__name__)




class CustomerRegistrationView(CreateView):
    model = User
    form_class = CustomerRegistrationForm
    template_name = 'user/customer_registration.html'
    success_url = reverse_lazy('user:login')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
      
        context['address_form'] = CustomerAddressAddForm()
        
        return context
    
    def form_valid(self, form):
        try:
            user = form.save()

            address_form = CustomerAddressAddForm(self.request.POST)
            if address_form.is_valid():
                customer =Customer.objects.create(user=user, address=address_form.cleaned_data['address'])
                
                logger.info(f'Registration of customer [{form.cleaned_data["username"]}] was successful.')

                return redirect(self.success_url)
            
        except OperationalError as e:
            logger.error(f'Failed creating customer, database operational error: {e}')
            messages.error(self.request, 'Sorry, something went wrong. Please try again later.')
            return redirect('main:home')

        except Exception as e:
            logger.exception(f'An unexpected error while creating customer: {e}')
            messages.error(self.request, 'Sorry, something went wrong. Please try again later.')
            return super().form_invalid(form)

        

    def form_invalid(self, form):

        logger.warning(f'Registration form invalid {form.errors}.')
        
        return super().form_invalid(form)
    



class RestaurantOwnerRegistrationView(CreateView):
    model = User
    form_class = RestaurantOwnerRegistrationForm
    template_name = 'user/restaurantowner_registration.html'
    success_url = reverse_lazy('user:login')


    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
        
            context['restaurant_owner_form'] = RestaurantOwnerInfoForm()
            
            return context


    def form_valid(self, form):
        try:
            user = form.save(commit=False)
            user.role = 'restaurant_owner'
            user.save()
            
            
            restaurant_owner_form = RestaurantOwnerInfoForm(self.request.POST)
            if restaurant_owner_form.is_valid():
                restaurant_owner = RestaurantOwner.objects.create(user=user, 
                            restaurant_name=restaurant_owner_form.cleaned_data['restaurant_name'],
                            restaurant_address=restaurant_owner_form.cleaned_data['restaurant_address'],
                            description=restaurant_owner_form.cleaned_data['description'],
                            )
            
            logger.info(f'Registration of restaurant owner [{form.cleaned_data["username"]}] was successful.')
            return redirect(self.success_url)
        
        except OperationalError as e:
            logger.info(f'Failed creating restaurant owner due to database operational error: {e}')

        except Exception as e:
            logger.exception(f'An unexpected error while creating restaurant owner: {e}')
            messages.error(self.request, "Sorry, something went wrong. Please try again later.")
            return super().form_invalid(form)
        
        

    def form_invalid(self, form):
        logger.warning(f'Registration form invalid {form.errors}.')
        return super().form_invalid(form)




class UserLoginView(LoginView):
    template_name = 'user/login.html'
    success_url = reverse_lazy('main:home')


    def form_valid(self, form):
        logger.info(f'User [{self.request.user.username}] logged in successfully.')
        return super().form_valid(form)
    
    
    def form_invalid(self, form):
        logger.warning(f'User login failed: {form.errors}')
        return super().form_invalid(form)
    


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('user:login')



class UserPasswordChangeView(PasswordChangeView):
    template_name = 'user/change_password.html'
    success_url = reverse_lazy('main:home')


    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user

        
        send_mail('Password Changed', f'Hello {user.username}, you successfully changed your password.',
                    settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)

        logger.info(f'User [{user.username}] changed their password successfully.')
        return response
    
    
    def form_invalid(self, form):
        logger.warning(f'Password change form invalid [{self.request.user.username}] failed: {form.errors}')
        return super().form_invalid(form)
    




class UserResetPasswordView(PasswordResetView):
    template_name = 'user/reset_password_request.html'
    email_template_name = 'user/reset_password_email.html'
    html_email_template_name = 'user/reset_password_email.html'
    success_url = reverse_lazy('main:home')


    def form_valid(self, form):
        logger.info(f'Password reset request sent for user [{form.cleaned_data.get("email")}].')
        return super().form_valid(form)


    def form_invalid(self, form):
        logger.warning(f'Password reset request form invalid: {form.errors}. Request info: {self.request.POST}')
        return super().form_invalid(form)
    



class UserResetPasswordConfirmView(PasswordResetConfirmView):
    template_name = 'user/reset_password_confirm.html'
    success_url = reverse_lazy('user:login')


    def form_valid(self, form):
        logger.info(f'Password reset for user [{form.cleaned_data.get('username')}] successful.')
        return super().form_valid(form)
    

    def form_invalid(self, form):
        logger.warning(f'Password reset form invalid: {form.errors}. Request info: {self.request.POST}')
        return super().form_invalid(form)
    



class CustomerProfileView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = 'user/customer_profile.html'
    context_object_name = 'customer'


    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        pk = self.kwargs.get('pk')
        customer = get_object_or_404(Customer, pk=pk)
        
        return customer
    

    def get(self, request, *args, **kwargs):
        logger.info(f'User [{request.user.username}] accessed customer profile page.')
        return super().get(request, *args, **kwargs)
    



class RestaurantOwnerProfileView(LoginRequiredMixin, DetailView):
    model = RestaurantOwner
    template_name = 'user/restaurantowner_profile.html'
    context_object_name = 'restaurant_owner'


    def get_object(self, queryset=None):
        return get_object_or_404(RestaurantOwner, user=self.request.user)
    
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurants = Restaurant.objects.filter(restaurant_owner=self.request.user)
        context['restaurants'] = restaurants
    
        menu_categories_by_restaurant = {}
        for restaurant in restaurants:
            menu_categories = MenuCategory.objects.filter(restaurant=restaurant)
            menu_categories_by_restaurant[restaurant] = menu_categories

        context['menu_categories_by_restaurant'] = menu_categories_by_restaurant
        return context

    

    def get(self, request, *args, **kwargs):
        logger.info(f'User [{request.user.username}] accessed restaurant owner profile page.')
        return super().get(request, *args, **kwargs)
    




class UpdateRestaurantOwnerView(LoginRequiredMixin, UpdateView):
    model = RestaurantOwner
    form_class = RestaurantOwnerUpdateForm
    template_name = 'user/restaurantowner_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant_owner = self.get_object()
        context['user_form'] = UserUpdateForm(instance=restaurant_owner.user)
        context['restaurant_owner_form'] = RestaurantOwnerInfoForm(instance=restaurant_owner)
        return context


    def get_success_url(self):
        return reverse_lazy('user:restaurantowner_profile', kwargs={'pk': self.object.pk})


    def form_valid(self, form):
        result = validate_profile_update(self.request, self.object, UserUpdateForm, RestaurantOwnerUpdateForm, self.get_success_url())
        if isinstance(result, dict):
            return self.form_invalid(form, result['user_form'], result['profile_form'])
        return result
    
    def form_invalid(self, form):
        logger.warning(f'Profile update form invalid {form.errors}.')
        return super().form_invalid(form)

        


class UpdateCustomerView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerUpdateForm
    template_name = 'user/customer_update.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_object()
        context['user_form'] = UserUpdateForm(instance=customer.user)
        context['customer_form'] = CustomerAddressAddForm(instance=customer)
        return context


    def get_success_url(self):
        return reverse_lazy('user:customer_profile', kwargs={'pk': self.object.pk})

    

    def form_valid(self, form):
        result = validate_profile_update(self.request, self.object, UserUpdateForm, CustomerUpdateForm, self.get_success_url())
        if isinstance(result, dict):
            return self.form_invalid(form, result['user_form'], result['profile_form'])
        return result

    

    def form_invalid(self, form):
        logger.warning(f'Profile update form invalid {form.errors}.')
        return super().form_invalid(form)
        




class DeleteAccountView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'user/confirm_delete.html'
    success_url = reverse_lazy('user:login')


    def form_valid(self, form):
        user = self.request.user
        username = user.username
        user.delete()

        logger.info(f'Account of user [{username}] deleted successfully.')
        return super().form_valid(form)
    
    

    
    








