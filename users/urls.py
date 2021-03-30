from django.urls import path
from .views import user_register, vendor_register

urlpatterns = [
    path('', user_register, name='register'),
    path('vendor/', vendor_register, name='vendor_register'),
]