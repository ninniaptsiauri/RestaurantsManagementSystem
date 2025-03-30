from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render,  get_object_or_404
from django.views.generic import ListView, DetailView
from restaurant.models import Restaurant, RestaurantCategory, MenuItem
from order.models import ShoppingCart
from django.db.models import Q, Exists, OuterRef
import logging


logger = logging.getLogger(__name__)




class RestaurantListView(ListView):
    model = Restaurant
    template_name = 'home/restaurant_list.html'
    context_object_name = 'restaurants'
    paginate_by = 8

    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            logger.info(f'Search Filter: "{query}"')
            restaurants = Restaurant.objects.filter(
                Q(name__icontains=query) | Q(menu_categories__name__icontains=query)).distinct()
        else:
            logger.info('Accessing restaurant list page')
            restaurants = Restaurant.objects.all().order_by('-add_time')
        
        return restaurants
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['restaurant_categories'] = RestaurantCategory.objects.all()
    
        return context
    
    

class RestaurantDetailView(DetailView):
    model = Restaurant
    template_name = 'home/restaurant_detail.html'
    

    def get(self, request, *args, **kwargs):
        logger.info(f"User [{request.user.username }] accessed the restaurant category list page.")
        return super().get(request, *args, **kwargs)
    


class RestaurantCategoryListView(ListView):
    model = RestaurantCategory
    template_name = 'home/restaurant_category_list.html'
    context_object_name = 'restaurant_categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['restaurant_categories'] = RestaurantCategory.objects.all()
        return context



class RestaurantByCategoryListView(ListView):
    model = Restaurant
    template_name = 'home/restaurant_list.html' 
    context_object_name = 'restaurants'
    paginate_by = 8

    def get_queryset(self):
        self.category = get_object_or_404(RestaurantCategory, pk=self.kwargs['pk'])
        return Restaurant.objects.filter(category=self.category) 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['restaurant_categories'] = RestaurantCategory.objects.all()
        context['category'] = self.category
        return context

    

class RestaurantCategoryDetailView(DetailView):
    model = RestaurantCategory
    template_name = 'home/restaurant_category_detail.html'
    context_object_name = 'restaurant_category'


\

    
    


    