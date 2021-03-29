from django.urls import path
from users.views import user_register

urlpatterns = [
    path('', user_register, name='register'),
]