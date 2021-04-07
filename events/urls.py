from django.urls import path
from .views import event_create, home_page, search_event, event_list, EventUpdateView, EventDeleteView, booking, booking_cart

urlpatterns = [
    path('', home_page, name='event-home'),
    path('add-events/', event_create, name='event-create'),
    path('event-list/', event_list, name='event-list'),
    path('<pk>/Update', EventUpdateView.as_view(), name='event-update'),
    path('<pk>/delete', EventDeleteView.as_view(), name='event-delete'),
    path('search/', search_event, name='search_results'),
    path('<pk>/booking', booking, name='event-booking'),
    path('cart/', booking_cart, name='cart'),
]