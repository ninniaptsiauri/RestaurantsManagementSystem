from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    path('shoppingcart/list/', views.ListShoppingCartView.as_view(), name='shopping_cart_list'),
    path('shoppingcart/detail/<int:pk>/', views.DetailShoppingCartView.as_view(), name='detail_shopping_cart'),
    path('shoppingcart/delete/<int:pk>/', views.DeleteShoppingCartView.as_view(), name='delete_shopping_cart'),
    path('add_to_cart/<int:item_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('shoppingcart/<int:cart_pk>/item/update/<int:pk>', views.UpdateShoppingCartItemView.as_view(), name='update_shopping_cart_item'),
    path('shoppingcart/item/delete/<int:pk>', views.DeleteShoppingCartItemView.as_view(), name='delete_shopping_cart_item'),
    path('shoppingcart/<int:cart_pk>/item/list/', views.ListShoppingCartItemView.as_view(), name='shopping_cart_item_list'),
    path('shoppingcart/<int:cart_pk>/item/detail/<int:pk>', views.DetailShoppingCartItemView.as_view(), name='detail_shopping_cart_item'),
    path('shoppingcart/<int:cart_pk>/checkout/', views.CheckoutShoppingCartView.as_view(), name='checkout'),
    path('order/confirm/<int:pk>/', views.OrderConfirmView.as_view(), name='order_confirm'),
    path('order/list/', views.OrderListView.as_view(), name='order_list'),
    
]
