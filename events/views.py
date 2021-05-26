from django.shortcuts import render, get_object_or_404, redirect
from users.models import Profile
from django.contrib.auth.models import User
from .forms import EventCreateForm, EventUpdateForm, EventBookingForm, EventReviewForm
from .models import Event, Booking, Review
from django.contrib import messages
from django.views.generic import UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponseNotFound
from django.db.models import Q
import json
from datetime import date

# Create your views here.

def home_page(request):
    if request.user.is_authenticated:
        admin = False
        if request.user.profile.is_admin:
            admin = True
            return render(request, 'events/index.html', {'admin' : admin})
        else:
            return render(request, 'events/index.html', {'admin' : admin})
    events = Event.objects.all()
    content = {
        'events':events,
    }

    return render(request, 'events/index.html', content)

@login_required
def search_event(request):
    user = request.user
    if user.profile.is_admin:
        messages.warning(request,"You need a customer account")
    else:
        if request.method == 'GET':    
            place =  request.GET.get('place')
            category = request.GET.get('category')
            object_list = Event.objects.filter(
                Q(place__icontains=place) & Q(category__contains=category)
            )

        return render(request, 'events/search_result.html', {'object':object_list})
    return render(request, 'events/search_result.html')


def event_details(request, pk):
    user = request.user
    event = Event.objects.get(id=pk)
    image = event.image.url
    reviews = Review.objects.filter(event=pk)
    rating = Review.objects.average_ratings(event)

    content = {
        'event' : event,
        'img' : image,
        'reviews' : reviews,
        'rating' : rating
    }
    return render(request, 'events/event_details.html', content)

def add_review(request, pk):
    user = request.user
    event = Event.objects.get(id=pk)
    if request.method == 'POST':
        form = EventReviewForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.customer = user
            instance.event = event
            instance.save()
            return redirect('event-details', pk=pk)

    form = EventReviewForm()
    content = {
        "form" : form
    }
    return render(request, 'events/review.html', content)

@login_required
def event_create(request):
    user = get_object_or_404(User, username=request.user)
    if user.profile.is_admin :
        if request.method == 'POST':
            event_form = EventCreateForm(request.POST, request.FILES)
            if event_form.is_valid():
                instance = event_form.save(commit=False)
                instance.user = user
                instance.save()
                post_added = True
                return redirect('event-home')
    else:
         return HttpResponseNotFound('<h1>404.Page not found</h1>')
    event_form = EventCreateForm()

    content = {
        'user' : request.user,
        'e_form' : event_form,
    }
    return render(request, 'events/add_event.html', content)

@login_required
def event_list(request):
    events = Event.objects.filter(user=request.user)

    content = {
        'events':events
    }

    return render(request, 'events/event_list.html', content)

class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventUpdateForm
    template_name = 'events/update.html'
    success_url = reverse_lazy('event-list')

    def form_valid(self, form):
        user = User.objects.get(username=self.request.user)
        if form.instance.user == user:
            return super().form_valid(form)
        else:
            form.add_error(None, 'You need to be the user to Update')
            return super().form_invalid(form)

class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    template_name = 'events/confirm_del.html'
    success_url = reverse_lazy('event-list')

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        obj = Event.objects.get(pk=pk)
        if not obj.user == self.request.user:
            messages.warning(self.request, "You need to be the owner.")
        return obj

@login_required
def booking(request, pk):
    user = request.user
    event = Event.objects.get(id=pk)
    f = Booking.objects.get_all_dates(event)
    dates_list = list(f)
    if user.profile.is_admin:
        messages.warning(request,"You need customer account")
    else:
        if request.method=='POST':
            form = EventBookingForm(request.POST)
            if form.is_valid():
                s_date = form.cleaned_data['start_date']
                e_date = form.cleaned_data['end_date']
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                qs = Booking.objects.check_availability(event,s_date,e_date)
                today = date.today()
                if not qs or s_date < today or e_date < today:
                    messages.warning(request,f'This service is not available on the selected dates')
                else:
                    instance = form.save(commit=False)
                    instance.customer = user
                    instance.event = event
                    instance.save()
                    return redirect('cart')
    form = EventBookingForm()
    context = {
        'form' : form,
        'event' : event,
        'dates' : json.dumps(dates_list),
        }
    return render(request, 'events/booking.html', context)

@login_required
def booking_cart(request):
    booking = Booking.objects.filter(customer=request.user)

    context = {
        'booking' : booking
    }
    return render(request, 'events/booking_list.html', context)