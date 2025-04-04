from django.urls import path
from . import views


app_name = 'restaurant'

urlpatterns = [
    path('add/', views.CreateRestaurantView.as_view(), name='add'),
    path('details/<int:pk>/', views.RestaurantDetailView.as_view(), name='restaurant_details'),
    path('update/<int:pk>/', views.UpdateRestaurantView.as_view(), name='update_restaurant'),
    path('delete/<int:pk>/', views.DeleteRestaurantView.as_view(), name='delete_restaurant'),
    path('menucategory/add/', views.CreateMenuCategoryView.as_view(), name='add_menu_category'),
    path('menucategory/update/<int:pk>/', views.UpdateMenuCategoryView.as_view(), name='update_menu_category'),
    path('menucategory/delete/<int:pk>/', views.DeleteMenuCategoryView.as_view(), name='delete_menu_category'),
    path('menu/categories/<int:restaurant_id>/', views.MenuCategoryListView.as_view(), name='menu_categories'),
    path('menuitem/add/<int:menu_category_id>/', views.CreateMenuItemView.as_view(), name='add_menu_item'),
    path('menuitems/<int:menu_category_id>/', views.MenuItemListView.as_view(), name='menu_items'),
    path('menuitem/details/<int:pk>/', views.MenuItemDetailsView.as_view(), name='menu_item_details'),
    path('menuitem/update/<int:pk>/', views.UpdateMenuItemView.as_view(), name='update_menu_item'),
    path('menuitem/delete/<int:pk>/', views.DeleteMenuItemView.as_view(), name='delete_menu_item'),
    path('menuitems/all/<int:restaurant_id>/', views.AllMenuItemsView.as_view(), name='all_menu_items'),
    path('table/create/<int:restaurant_id>/', views.CreateTableView.as_view(), name='create_table'),
    path('table/list/<int:restaurant_id>/', views.TableListView.as_view(), name='table_list'),
    path('table/details/<int:pk>/', views.TableDetailView.as_view(), name='table_details'),
    path('table/update/<int:pk>/', views.UpdateTableView.as_view(), name='update_table'),
    path('table/delete/<int:pk>/', views.DeleteTableView.as_view(), name='delete_table'),
    path('orders/', views.RestaurantOrderView.as_view(), name='restaurant_orders'),
    path('reservations/', views.RestaurantReservationView.as_view(), name='restaurant_reservations'),
    
]