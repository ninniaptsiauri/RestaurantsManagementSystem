from django.urls import path
from . import views

app_name = 'reservation'

urlpatterns = [
    path('create/<int:restaurant_id>/<int:table_id>/', views.CreateReservation.as_view(), name='create'),
    path('update/<int:pk>/', views.UpdateReservation.as_view(), name='update'),
    path('list/', views.ReservationListView.as_view(), name='list'),
    path('detail/<int:pk>/', views.ReservationDetailView.as_view(), name='detail'),
    path('delete/<int:pk>/', views.DeleteReservationView.as_view(), name='delete'),
    path('cancel/<int:pk>/', views.CancelReservationView.as_view(), name='cancel')
]

