from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('<int:pk>/favourites/', views.add_favourites, name='add_favourites'),
    path('vendor/register', views.vendor_register, name='vendor_register'),
    path('vendor/login', views.vendor_login, name='vendor_login'),
    path('forgot-password/', views.ForgotPassword, name='forgot-password'),
    path('password-reset-sent/',auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_sent.html'), name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.ResetPassword, name='reset-password'),
    path('favourites/', views.favourites_list, name='favourites_list'),

]