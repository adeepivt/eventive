from django.urls import path
from .views import user_register, user_login, vendor_register, vendor_login

urlpatterns = [
    path('', user_register, name='register'),
    path('login/', user_login, name='login'),
    path('vendor/register', vendor_register, name='vendor_register'),
    path('vendor/login', vendor_login, name='vendor_login'),
]