from django.shortcuts import render, get_object_or_404, redirect
from users.models import Profile
from django.contrib.auth.models import User
from .forms import EventCreateForm, EventUpdateForm
from .models import Event
from django.contrib import messages
from django.views.generic import UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponseNotFound
from django.db.models import Q

# Create your views here.

def home_page(request):
    events = Event.objects.all()
    content = {
        'events':events,
    }

    return render(request, 'events/index.html', content)

@login_required
def search_event(request):
    if request.method == 'GET':    
        place =  request.GET.get('place')
        category = request.GET.get('category')
        object_list = Event.objects.filter(
            Q(place__icontains=place) & Q(category__contains=category)
        )

    return render(request, 'events/search_result.html', {'object':object_list})

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