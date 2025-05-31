from django.urls import path
from .views import * 

urlpatterns = [
    path('', home_page, name='event-home'),
    path('add-events/', event_create, name='event-create'),
    path('event-list/', event_list, name='event-list'), 
    path('<pk>/event-info/', event_details, name='event-details'),
    path('search/', search_event, name='search_results'),
    path('<pk>/Update', EventUpdateView.as_view(), name='event-update'),
    path('<pk>/delete', delete_transaction, name='event-delete'),
    path('event/<int:event_id>/check-availability/', check_availability_htmx, name='check_availability_htmx'),
    path('events/<int:event_id>/book/', booking_form, name='create_booking'),
    path('booking/success/<int:booking_id>/', booking_success, name='booking_success'),
]