from django.urls import path
from . import views


app_name = 'main'

urlpatterns = [
    path('', views.RestaurantListView.as_view(), name='home'),
    path('categories/', views.RestaurantCategoryListView.as_view(), name='restaurant_categories'),
    path('category/<int:pk>/', views.RestaurantByCategoryListView.as_view(), name='restaurant_category')
]
