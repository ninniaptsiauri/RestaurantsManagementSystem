from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from . models import Restaurant, RestaurantCategory, MenuCategory, MenuItem, Table
from . forms import RestaurantForm, MenuCategoryForm, MenuItemForm, TableForm
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from order.models import Order
from reservation.models import Reservation
from django.db import OperationalError
import logging
from django.contrib import messages
from .utils import handle_error



logger = logging.getLogger(__name__)



class CreateRestaurantView(PermissionRequiredMixin, CreateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = 'restaurant/create_restaurant.html'
    success_url = reverse_lazy('main:home')
    permission_required = 'restaurant.add_restaurant'


    def form_valid(self, form):
        if hasattr(self.request.user, 'restaurantowner'):
            try:
                form.instance.restaurant_owner = self.request.user
                restaurant = form.save()

            except Exception as e:
                return handle_error(self.request, e, 'creating Restaurant')
            
            else:
                logger.info(f'Restaurant "{form.cleaned_data["name"]}" created by [{self.request.user.username}] successfully.')
                return super().form_valid(form)
        
        else:
            return self.handle_no_permission()  
        


    def form_invalid(self, form):
        logger.info(f'Restaurant creation failed by [{self.request.user.username}]. {form.errors}')
        return super().form_invalid(form)




class RestaurantDetailView(DetailView):
    model = Restaurant
    template_name = 'restaurant/restaurant_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant = self.get_object()
        menu_categories = MenuCategory.objects.filter(restaurant=restaurant)
        tables = Table.objects.filter(restaurant=restaurant)
        context['menu_categories'] = menu_categories
        context['has_tables'] = tables.exists()
    
        return context
    

    def get(self, request, *args, **kwargs):
        restaurant = self.get_object()
        logger.info(f'User [{request.user.username}] accessed restaurant details (ID: {restaurant.pk}, Name: {restaurant.name}).')
        return super().get(request, *args, **kwargs)
    


class RestaurantOrderView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'restaurant/restaurant_orders.html'
    context_object_name = 'restaurant_orders'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        restaurants = Restaurant.objects.filter(restaurant_owner=user)
        
        queryset = Order.objects.filter(restaurant__in=restaurants).order_by('-order_date')
        return queryset
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        restaurants = Restaurant.objects.filter(restaurant_owner=user)
        context['restaurants'] = restaurants
        return context
    

    def get(self, request, *args, **kwargs):
        logger.info(f'User [{request.user.username}] accessed restaurant order list.')
        return super().get(request, *args, **kwargs)
    


class RestaurantReservationView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'restaurant/restaurant_reservations.html'
    context_object_name = 'restaurant_reservations'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        restaurants = Restaurant.objects.filter(restaurant_owner=user)
        tables = Table.objects.filter(restaurant__in=restaurants)
        
        queryset = Reservation.objects.filter(restaurant__in=restaurants).order_by('-reservation_date')
        return queryset
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        restaurants = Restaurant.objects.filter(restaurant_owner=user)
        context['restaurants'] = restaurants
        return context
    
    
    def get(self,request, *args, **kwargs):
        logger.info(f'User [{request.user.username}] accessed restaurant reservation list.')
        return super().get(request, *args, **kwargs)
    
 


class UpdateRestaurantView(PermissionRequiredMixin, UpdateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = 'restaurant/update_restaurant.html'
    permission_required = 'restaurant.change_restaurant'

    def form_valid(self, form):
        try:
            restaurant = form.save()

        except Exception as e:
            return handle_error(self.request, e, 'updating Restaurant')
        
        else:
            logger.info(f'Restaurant "{self.object.name}" updated successfully.')
            return super().form_valid(form)
    
    
    def form_invalid(self, form):
        logger.info(f'Restaurant {self.object.name} update  failed. Errors: {form.errors}')
        return super().form_invalid(form)
        
    
    
    def get_success_url(self):
        return reverse_lazy('restaurant:restaurant_details', kwargs={'pk': self.object.pk})



class DeleteRestaurantView(PermissionRequiredMixin, DeleteView):
    model = Restaurant
    success_url = reverse_lazy('main:home')
    template_name = 'restaurant/confirm_delete.html'
    permission_required = 'restaurant.delete_restaurant'


    def form_valid(self, form):
        logger.info(f'Restaurant "{self.object.name}" deleted successfully.')
        return super().form_valid(form)
        




class CreateMenuCategoryView(PermissionRequiredMixin, CreateView):
    model = MenuCategory
    template_name = 'restaurant/create_menu_category.html'
    permission_required = 'restaurant.add_menucategory'
    
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
        
    
    def get_form_class(self):
        return MenuCategoryForm
        

    def form_valid(self, form):
        try:
            menu_category = form.save()

        except Exception as e:
            return handle_error(self.request, e, 'creating Menu Category')

        else:
            self.restaurant = form.cleaned_data['restaurant']

            logger.info(f'Menu category "{form.cleaned_data["name"]}" created successfully by user [{self.request.user.username}].')
            return super().form_valid(form)
        


    def form_invalid(self, form):
        logger.info(f'Menu category creation failed by user [{self.request.user.username}]. Errors: {form.errors}')
        return super().form_invalid(form)
    


    def get_success_url(self):
        return reverse_lazy('restaurant:restaurant_details', kwargs={'pk': self.restaurant.pk})

    

class MenuCategoryListView(ListView):
    model = MenuCategory
    template_name = 'restaurant/menu_category_list.html'
    context_object_name = 'menu_categories'


    def get_queryset(self):
        restaurant_id = self.kwargs['restaurant_id']
        restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
        return MenuCategory.objects.filter(restaurant=restaurant)
    
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant = get_object_or_404(Restaurant, pk=self.kwargs['restaurant_id'])
        context['restaurant'] = restaurant
        return context

    
    def get(self, request, *args, **kwargs):
        logger.info(f'User [{request.user.username}] accessed menu category list (ID: {self.kwargs["restaurant_id"]}).)')
        return super().get(request, *args, **kwargs)
    




class UpdateMenuCategoryView(PermissionRequiredMixin, UpdateView):
    model = MenuCategory
    template_name = 'restaurant/update_menu_category.html'
    permission_required = 'restaurant.change_menucategory'
    success_url = reverse_lazy('main:home')
    

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    
    def get_form_class(self):
        return MenuCategoryForm
    

    def form_valid(self, form):
        try:
            menu_category = form.save()
        
        except Exception as es:
            return handle_error(self.request, e, 'updating Menu Category')
        
        else:
            logger.info(f'Menu category "{self.object.name}" updated successfully by user [{self.request.user.username}]')
            return super().form_valid(form)
    

    def form_invalid(self, form):
        logger.warning(f'Menu category "{self.object.name}" update failed by user [{self.request.user.username}]. Errors: {form.errors}')
        return super().form_invalid(form)



class DeleteMenuCategoryView(PermissionRequiredMixin, DeleteView):
    model = MenuCategory
    template_name = 'restaurant/confirm_delete.html'
    permission_required = 'restaurant.delete_menucategory'
    success_url = reverse_lazy('main:home')


    def form_valid(self, form):
        logger.info(f'Menu category "{self.object.name}" deleted successfully by user [{self.request.user.username}].')
        return super().form_valid(form)
    

    def get_success_url(self):
        restaurant_id = self.object.restaurant.id
        return reverse_lazy('restaurant:restaurant_details', kwargs={'pk': restaurant_id})
    



class CreateMenuItemView(PermissionRequiredMixin, CreateView):
    model = MenuItem
    template_name = 'restaurant/create_menu_item.html'
    permission_required = 'restaurant.add_menuitem'
    

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        menu_category_id = self.kwargs['menu_category_id']
        menu_category = get_object_or_404(MenuCategory, pk=menu_category_id)
        kwargs['menu_category'] = menu_category
        return kwargs
        
    
    def get_form_class(self):
        return MenuItemForm
        

    def form_valid(self, form):
        try:
            menu_item = form.save()

        except Exception as e:
            return handle_error(self.request, e, 'creating Menu Item')

        else:
            logger.info(f'Menu item "{form.cleaned_data["name"]}" created successfully by user [{self.request.user.username}]')
            return super().form_valid(form)


    def form_invalid(self, form):
        logger.warning(f'Menu item creation failed by user [{self.request.user.username}]. Errors: {form.errors}')
        return super().form_invalid(form)


    def get_success_url(self):
        menu_category_id = self.kwargs['menu_category_id']
        return reverse_lazy('restaurant:menu_items', kwargs={'menu_category_id': menu_category_id})

    

class MenuItemListView(ListView):
    model = MenuItem
    template_name = 'restaurant/menu_item_list.html'
    context_object_name = 'menu_items'


    def get_queryset(self):
        menu_category_id = self.kwargs['menu_category_id']
        menu_category = get_object_or_404(MenuCategory, pk=menu_category_id)
        return MenuItem.objects.filter(category=menu_category)
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        menu_category_id = self.kwargs['menu_category_id']
        menu_category = get_object_or_404(MenuCategory, pk=menu_category_id)
        context['menu_category'] = menu_category

        logger.info(f"Successfully opened menu category: (ID: {menu_category_id}) by user [{self.request.user.username}]")

        return context
    
    


class MenuItemDetailsView(DetailView):
    model = MenuItem
    template_name = 'restaurant/menu_item_details.html'
    context_object_name = 'menu_item'




class UpdateMenuItemView(PermissionRequiredMixin, UpdateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'restaurant/update_menu_item.html'
    permission_required = 'restaurant.change_menuitem'
    

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        menu_item = self.get_object()
        kwargs['menu_category'] = menu_item.category
        return kwargs
    

    def form_valid(self, form):
        try:
            menu_item = form.save()

        except Exception as e:
            return handle_error(self.request, e, 'updating Menu Item')

        else:
            logger.info(f'Menu item (ID: {self.object.pk}) updated successfully by user [{self.request.user.username}]')
            return super().form_valid(form)
        

    def form_invalid(self, form):
        logger.warning(f'Menu item (ID: {self.object.pk}) update failed. Errors: {form.errors}')
        return super().form_invalid(form)


    def get_success_url(self):
        menu_item = self.get_object()
        return reverse_lazy('restaurant:menu_item_details', kwargs={'pk': menu_item.pk})
    


class DeleteMenuItemView(PermissionRequiredMixin, DeleteView):
    model = MenuItem
    template_name = 'restaurant/confirm_delete.html'
    permission_required = 'restaurant.delete_menuitem'

    
    def get_success_url(self):
        menu_item = self.get_object()
        return reverse_lazy('restaurant:menu_items', kwargs={'menu_category_id': menu_item.category.id})

    




class CreateTableView(PermissionRequiredMixin, CreateView):
    model = Table
    form_class = TableForm
    template_name = 'restaurant/create_table.html'
    permission_required = 'restaurant.add_table'


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
        
    
    def get_form_class(self):
        return TableForm
    
    def form_valid(self, form):
        try:
            table = form.save()

        except Exception as e:
            return handle_error(self.request, e, 'creating Table')
            

        else:
            logger.info(f'Table created successfully by user [{self.request.user.username}]')
            return super().form_valid(form)
        

    def form_invalid(self, form):
        logger.warning(f'Table create form invalid by user [{self.request.user.username}]. Errors: {form.errors}]')
        return super().form_invalid(form)
    
    

    def get_success_url(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        return reverse_lazy('restaurant:table_list', kwargs={'restaurant_id': restaurant_id})
    


class TableListView(ListView):
    model = Table
    template_name = 'restaurant/table_list.html'
    context_object_name = 'tables'


    def get_queryset(self):
        restaurant_id = self.kwargs['restaurant_id']
        return Table.objects.filter(restaurant_id=restaurant_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant_id = self.kwargs['restaurant_id']
        restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
        context['restaurant'] = restaurant
        return context
    
    


class TableDetailView(DetailView):
    model = Table
    template_name = 'restaurant/table_detail.html'
    context_object_name = 'table'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = self.get_object()
        context['restaurant'] = table.restaurant

        logger.info(f'User [{self.request.user.username}] accessed table details (ID: {table.pk})')
        return context
    


class UpdateTableView(PermissionRequiredMixin, UpdateView):
    model = Table
    form_class = TableForm
    template_name = 'restaurant/update_table.html'
    permission_required = 'restaurant.change_table'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    

    def form_valid(self, form):
        try:
            table = form.save()
        
        except Exception as e:
           return handle_error(self.request, e, 'updating Table')
        

        else:
            logger.info(f'Table (ID: {self.object.id}) updated successfully by user [{self.request.user.username}]')
            return super().form_valid(form)
    


    def form_invalid(self, form):
        logger.warning(f'Table (ID: {self.object.id}) update failed by user [{self.request.user.username}]. Errors: {form.errors}')
        return super().form_invalid(form)


    def get_success_url(self):
        return reverse_lazy(
            'restaurant:table_details',
            kwargs={'pk': self.object.pk}
        )
    



class DeleteTableView(PermissionRequiredMixin, DeleteView):
    model = Table
    template_name = 'restaurant/confirm_delete.html'
    permission_required = 'restaurant.delete_table'
    
    def get_success_url(self):
        return reverse_lazy(
            'restaurant:table_list',
            kwargs={'restaurant_id': self.object.restaurant.pk}
        )
    

