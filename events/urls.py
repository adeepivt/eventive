from django.urls import path
from .views import event_create, home_page, search_event, event_list, EventUpdateView, EventDeleteView

urlpatterns = [
    path('', home_page, name='event-home'),
    path('add-events/', event_create, name='event-create'),
    path('event-list/', event_list, name='event-list'),
    path('<pk>/Update', EventUpdateView.as_view(), name='event-update'),
    path('<pk>/delete', EventDeleteView.as_view(), name='event-delete'),
    path('search/', search_event, name='search_results'),
]