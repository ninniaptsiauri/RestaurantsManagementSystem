from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('customer_registration/', views.CustomerRegistrationView.as_view(), name='customer_registration'),
    path('restaurantowner_registration/', views.RestaurantOwnerRegistrationView.as_view(), name='restaurantowner_registration'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('change_password/', views.UserPasswordChangeView.as_view(), name='change_password'),
    path('reset_password_request/', views.UserResetPasswordView.as_view(), name='reset_password_request'),
    path('reset_password_confirm/<uidb64>/<token>/', views.UserResetPasswordConfirmView.as_view(), name='reset_password_confirm'),
    path('customer/profile/<int:pk>/', views.CustomerProfileView.as_view(), name='customer_profile'),
    path('restaurant_owner/profile/<int:pk>/', views.RestaurantOwnerProfileView.as_view(), name='restaurantowner_profile'),
    path('customer/edit_profile/<int:pk>/', views.UpdateCustomerView.as_view(), name='customer_edit_profile'),
    path('restaurant_owner/edit_profile/<int:pk>/', views.UpdateRestaurantOwnerView.as_view(), name='restaurantowner_edit_profile'),
    path('delete_account/<int:pk>/', views.DeleteAccountView.as_view(), name='delete_account'),
    
    
]