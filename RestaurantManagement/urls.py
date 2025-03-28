
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls', namespace='main')),
    path('user/', include('user.urls', namespace='user')),
    path('restaurant/', include('restaurant.urls', namespace='restaurant')),
    path('order/', include('order.urls', namespace='order')),
    path('reservation/', include('reservation.urls', namespace='reservation')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)