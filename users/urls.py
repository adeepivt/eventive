from django.urls import path
from .views import user_register, user_login, vendor_register, vendor_login, add_favourites, favourites_list

urlpatterns = [
    path('', user_register, name='register'),
    path('login/', user_login, name='login'),
    path('<int:pk>/favourites/', add_favourites, name='add_favourites'),
    path('favourites/', favourites_list, name='favourites_list'),
    path('vendor/register', vendor_register, name='vendor_register'),
    path('vendor/login', vendor_login, name='vendor_login'),
]