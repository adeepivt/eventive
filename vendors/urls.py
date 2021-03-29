from django.urls import path
from .views import vendor_register


urlpatterns = [
    path('', vendor_register, name='vendor_register'),
]
