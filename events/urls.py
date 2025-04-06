from django.urls import path
from .views import ( home_page, event_create, event_list, event_details, EventUpdateView, delete_transaction, search_event )

urlpatterns = [
    path('', home_page, name='event-home'),
    path('add-events/', event_create, name='event-create'),
    path('event-list/', event_list, name='event-list'), 
    path('<pk>/event-info/', event_details, name='event-details'),
    path('search/', search_event, name='search_results'),
    path('<pk>/Update', EventUpdateView.as_view(), name='event-update'),
    path('<pk>/delete', delete_transaction, name='event-delete'),
]